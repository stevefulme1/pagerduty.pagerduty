"""
pagerduty_normalize.py - EDA event filter that normalizes PagerDuty V3 webhook payloads.

Transforms the deeply nested PagerDuty V3 webhook JSON structure into a flat
dictionary of well-known fields.  Designed for use after a generic webhook
source (e.g. ``ansible.eda.webhook``) receives the raw POST body.

The filter looks for the V3 envelope at ``event.payload.event`` or at the
top-level ``event`` key and extracts incident metadata into flat fields.

Output fields:
    event_type        - e.g. "incident.triggered"
    incident_id       - PagerDuty incident ID
    incident_title    - Short incident summary
    incident_status   - triggered / acknowledged / resolved
    incident_urgency  - high / low
    priority_name     - Priority label (e.g. "P1")
    service_name      - Originating service display name
    service_id        - PagerDuty service ID
    assignee_names    - List of assignee display names
    assignee_emails   - List of assignee contact emails
    html_url          - Browser link to the incident

Example rulebook usage:
    sources:
      - ansible.eda.webhook:
          host: 0.0.0.0
          port: 5000
    filters:
      - pagerduty.pagerduty.pagerduty_normalize:
"""

import logging
from typing import Any

logger = logging.getLogger("pagerduty.pagerduty.pagerduty_normalize")


def _extract_event_body(event: dict) -> dict | None:
    """Locate the PagerDuty event body within the webhook payload.

    V3 webhooks wrap events as ``{"event": {<event_body>}}``.
    When received via ``ansible.eda.webhook`` the outer wrapper may
    be at ``event["payload"]["event"]`` or ``event["event"]``.
    """
    # Path 1: ansible.eda.webhook nests the POST body under "payload"
    payload = event.get("payload", {})
    if isinstance(payload, dict) and "event" in payload:
        return payload["event"]

    # Path 2: event already is the top-level webhook JSON
    if "event" in event:
        return event["event"]

    # Path 3: the event dict itself might already be the event body
    if "type" in event and "data" in event:
        return event

    return None


def _normalize(event_body: dict) -> dict:
    """Build flat fields from a PagerDuty V3 event body."""
    incident = event_body.get("data", {})
    service = incident.get("service", {})
    priority = incident.get("priority", {}) or {}

    assignees = incident.get("assignees", [])
    assignee_names = [a.get("summary", "") for a in assignees if a.get("summary")]

    # Attempt to extract emails from the self URL or contact info
    assignee_emails = [
        a.get("html_url", "").rstrip("/").rsplit("/", 1)[-1]
        for a in assignees
        if a.get("html_url")
    ]

    return {
        "event_type": event_body.get("type", ""),
        "incident_id": incident.get("id", ""),
        "incident_title": incident.get("title", ""),
        "incident_status": incident.get("status", ""),
        "incident_urgency": incident.get("urgency", ""),
        "priority_name": priority.get("summary", ""),
        "service_name": service.get("summary", ""),
        "service_id": service.get("id", ""),
        "assignee_names": assignee_names,
        "assignee_emails": assignee_emails,
        "html_url": incident.get("html_url", ""),
    }


def main(event: dict[str, Any], **kwargs) -> dict[str, Any] | None:
    """EDA event filter entry point.

    Locates the PagerDuty V3 event body within *event*, normalizes it
    into flat fields, and merges the result back into the event dict.
    The original payload is preserved under ``raw_event``.

    Returns ``None`` if the payload cannot be recognized as a PagerDuty
    V3 webhook delivery, which causes EDA to drop the event.
    """
    event_body = _extract_event_body(event)
    if event_body is None:
        logger.warning("Could not locate PagerDuty event body — dropping event")
        return None

    normalized = _normalize(event_body)
    normalized["raw_event"] = event
    return normalized
