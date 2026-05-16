"""
pagerduty_webhook.py - EDA source plugin for PagerDuty V3 webhooks.

Runs an async HTTP server that receives PagerDuty V3 webhook POST requests,
validates the HMAC-SHA256 signature, normalizes the nested payload into flat
event fields, and pushes events onto the EDA queue.

Arguments:
    host:        Bind address (default: 0.0.0.0)
    port:        Listen port (default: 5000)
    token:       Webhook signing secret for HMAC-SHA256 validation (required)
    event_types: Optional list of event types to accept (e.g. ["incident.triggered"])
    certfile:    Optional path to TLS certificate file
    keyfile:     Optional path to TLS private key file

Example rulebook usage:
    sources:
      - pagerduty.pagerduty.pagerduty_webhook:
          host: 0.0.0.0
          port: 5000
          token: "{{ PAGERDUTY_WEBHOOK_SECRET }}"
          event_types:
            - incident.triggered
            - incident.acknowledged
"""

import asyncio
import hashlib
import hmac
import json
import logging
import ssl
from typing import Any

from aiohttp import web

logger = logging.getLogger("pagerduty.pagerduty.pagerduty_webhook")


def _normalize_incident(event_body: dict) -> dict:
    """Extract flat fields from a PagerDuty V3 webhook event body."""
    event_type = event_body.get("type", "")
    incident = event_body.get("data", {})

    assignees = incident.get("assignees", [])
    assignee_names = [a.get("summary", "") for a in assignees if a.get("summary")]

    service = incident.get("service", {})
    priority = incident.get("priority", {}) or {}

    return {
        "event_type": event_type,
        "incident_id": incident.get("id", ""),
        "incident_title": incident.get("title", ""),
        "incident_status": incident.get("status", ""),
        "incident_urgency": incident.get("urgency", ""),
        "priority_name": priority.get("summary", ""),
        "service_name": service.get("summary", ""),
        "service_id": service.get("id", ""),
        "assignee_names": assignee_names,
        "html_url": incident.get("html_url", ""),
    }


def _verify_signature(body: bytes, signature_header: str, secret: str) -> bool:
    """Verify the PagerDuty V3 webhook HMAC-SHA256 signature.

    PagerDuty sends the header as ``v1=<hex_digest>``.
    """
    if not signature_header or not signature_header.startswith("v1="):
        return False

    expected_sig = signature_header[3:]
    computed = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, expected_sig)


async def _webhook_handler(
    request: web.Request,
    queue: asyncio.Queue,
    token: str,
    event_types: list[str] | None,
) -> web.Response:
    """Handle an incoming PagerDuty webhook POST request."""
    if request.method != "POST":
        return web.Response(status=405, text="Method Not Allowed")

    body = await request.read()

    # Validate signature
    sig_header = request.headers.get("X-PagerDuty-Signature", "")
    if not _verify_signature(body, sig_header, token):
        logger.warning("Invalid or missing webhook signature — rejecting request")
        return web.Response(status=401, text="Invalid signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Failed to decode webhook JSON payload")
        return web.Response(status=400, text="Invalid JSON")

    # PagerDuty V3 webhooks wrap events in {"event": {...}}
    event_body = payload.get("event", {})
    event_type = event_body.get("type", "")

    if event_types and event_type not in event_types:
        logger.debug("Ignoring event type %s (not in filter list)", event_type)
        return web.Response(status=202, text="Filtered")

    normalized = _normalize_incident(event_body)
    normalized["raw_event"] = payload

    await queue.put(normalized)
    logger.info("Queued event: %s for incident %s", event_type, normalized["incident_id"])

    return web.Response(status=200, text="OK")


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """EDA source plugin entry point.

    Starts an aiohttp server that listens for PagerDuty V3 webhook
    deliveries and pushes normalized events onto the EDA queue.
    """
    host = str(args.get("host", "0.0.0.0"))
    port = int(args.get("port", 5000))
    token = str(args.get("token", ""))
    event_types = args.get("event_types")
    certfile = args.get("certfile")
    keyfile = args.get("keyfile")

    if not token:
        raise ValueError("'token' (webhook signing secret) is required")

    app = web.Application()
    app.router.add_post(
        "/",
        lambda req: _webhook_handler(req, queue, token, event_types),
    )

    ssl_ctx = None
    if certfile and keyfile:
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_ctx.load_cert_chain(certfile, keyfile)
        logger.info("TLS enabled with cert=%s key=%s", certfile, keyfile)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port, ssl_context=ssl_ctx)
    await site.start()

    logger.info("PagerDuty webhook listener started on %s:%d", host, port)

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    """Entry point for standalone testing."""

    class _MockQueue:
        async def put(self, item):
            print(json.dumps(item, indent=2))

    asyncio.run(main(_MockQueue(), {"token": "test-secret", "port": 5000}))
