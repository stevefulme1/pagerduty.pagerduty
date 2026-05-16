"""
pagerduty_api.py - EDA source plugin that polls PagerDuty REST API for incidents.

Periodically polls the PagerDuty ``GET /incidents`` endpoint and emits events
when new incidents appear or existing incidents change status.

Arguments:
    api_token:      PagerDuty REST API token (required)
    poll_interval:  Seconds between polls (default: 30)
    service_ids:    Optional list of service IDs to filter
    statuses:       Status filter list (default: ["triggered", "acknowledged"])
    urgencies:      Optional list of urgencies to filter (e.g. ["high"])
    api_url:        PagerDuty API base URL (default: https://api.pagerduty.com)

Example rulebook usage:
    sources:
      - pagerduty.pagerduty.pagerduty_api:
          api_token: "{{ PAGERDUTY_API_TOKEN }}"
          poll_interval: 30
          service_ids:
            - P1234AB
          statuses:
            - triggered
            - acknowledged
"""

import asyncio
import logging
from typing import Any

import aiohttp

logger = logging.getLogger("pagerduty.pagerduty.pagerduty_api")

_DEFAULT_API_URL = "https://api.pagerduty.com"
_DEFAULT_STATUSES = ["triggered", "acknowledged"]


def _normalize_incident(incident: dict, event_type: str) -> dict:
    """Build a flat event dict from a PagerDuty incident object."""
    service = incident.get("service", {})
    priority = incident.get("priority", {}) or {}
    assignees = incident.get("assignments", [])
    assignee_names = [
        a.get("assignee", {}).get("summary", "")
        for a in assignees
        if a.get("assignee", {}).get("summary")
    ]
    assignee_emails = [
        a.get("assignee", {}).get("html_url", "")
        for a in assignees
    ]

    return {
        "event_type": event_type,
        "incident_id": incident.get("id", ""),
        "incident_number": incident.get("incident_number"),
        "incident_title": incident.get("title", ""),
        "incident_status": incident.get("status", ""),
        "incident_urgency": incident.get("urgency", ""),
        "priority_name": priority.get("summary", ""),
        "service_name": service.get("summary", ""),
        "service_id": service.get("id", ""),
        "assignee_names": assignee_names,
        "assignee_emails": assignee_emails,
        "html_url": incident.get("html_url", ""),
        "created_at": incident.get("created_at", ""),
        "updated_at": incident.get("last_status_change_at", ""),
        "raw_incident": incident,
    }


async def _fetch_incidents(
    session: aiohttp.ClientSession,
    api_url: str,
    api_token: str,
    statuses: list[str],
    service_ids: list[str] | None,
    urgencies: list[str] | None,
) -> list[dict]:
    """Fetch incidents from the PagerDuty REST API."""
    headers = {
        "Authorization": f"Token token={api_token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.pagerduty+json;version=2",
    }

    params: dict[str, Any] = {
        "statuses[]": statuses,
        "sort_by": "created_at:desc",
        "limit": 100,
    }
    if service_ids:
        params["service_ids[]"] = service_ids
    if urgencies:
        params["urgencies[]"] = urgencies

    url = f"{api_url}/incidents"
    incidents: list[dict] = []

    try:
        async with session.get(url, headers=headers, params=params) as resp:
            if resp.status != 200:
                body = await resp.text()
                logger.error("PagerDuty API returned %d: %s", resp.status, body)
                return []
            data = await resp.json()
            incidents = data.get("incidents", [])
    except aiohttp.ClientError as exc:
        logger.error("Error fetching PagerDuty incidents: %s", exc)

    return incidents


async def main(queue: asyncio.Queue, args: dict[str, Any]) -> None:
    """EDA source plugin entry point.

    Polls the PagerDuty REST API at the configured interval and emits
    events for new incidents or status changes.
    """
    api_token = str(args.get("api_token", ""))
    poll_interval = int(args.get("poll_interval", 30))
    service_ids = args.get("service_ids")
    statuses = args.get("statuses", _DEFAULT_STATUSES)
    urgencies = args.get("urgencies")
    api_url = str(args.get("api_url", _DEFAULT_API_URL)).rstrip("/")

    if not api_token:
        raise ValueError("'api_token' is required")

    # Track incidents we have already seen: incident_id -> last known status
    seen: dict[str, str] = {}

    logger.info(
        "PagerDuty API poller starting (interval=%ds, statuses=%s)",
        poll_interval,
        statuses,
    )

    async with aiohttp.ClientSession() as session:
        while True:
            incidents = await _fetch_incidents(
                session, api_url, api_token, statuses, service_ids, urgencies
            )

            for incident in incidents:
                inc_id = incident.get("id", "")
                inc_status = incident.get("status", "")

                if inc_id not in seen:
                    event = _normalize_incident(incident, "incident.new")
                    await queue.put(event)
                    seen[inc_id] = inc_status
                    logger.info("New incident %s: %s", inc_id, incident.get("title"))

                elif seen[inc_id] != inc_status:
                    event = _normalize_incident(incident, "incident.changed")
                    event["previous_status"] = seen[inc_id]
                    await queue.put(event)
                    seen[inc_id] = inc_status
                    logger.info(
                        "Incident %s status changed: %s -> %s",
                        inc_id,
                        event["previous_status"],
                        inc_status,
                    )

            # Prune resolved incidents from the seen cache to avoid unbounded growth.
            # Keep only IDs that appeared in the latest poll.
            current_ids = {i.get("id") for i in incidents}
            stale = [k for k in seen if k not in current_ids]
            for k in stale:
                del seen[k]

            await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    import json

    class _MockQueue:
        async def put(self, item):
            print(json.dumps(item, indent=2, default=str))

    asyncio.run(
        main(
            _MockQueue(),
            {"api_token": "test", "poll_interval": 10},
        )
    )
