"""
pagerduty_enrich.py - EDA event filter that enriches PagerDuty events via REST API.

Calls the PagerDuty REST API to fetch additional context for an incident and
merges the results into the event dictionary.  Designed to run after
``pagerduty_normalize`` or the ``pagerduty_webhook`` source plugin so that
``incident_id`` is already a top-level field.

Arguments:
    api_token:  PagerDuty REST API token (required)
    include:    List of enrichment types to fetch.  Supported values:
                  - alerts          Alerts tied to the incident
                  - log_entries     Timeline / log entries
                  - notes           Incident notes
                  - service_details Full service object
                  - on_calls        Current on-call schedule for the service

Example rulebook usage:
    filters:
      - pagerduty.pagerduty.pagerduty_enrich:
          api_token: "{{ PAGERDUTY_API_TOKEN }}"
          include:
            - alerts
            - notes
            - on_calls
"""

import logging
import re
from typing import Any

import requests

logger = logging.getLogger("pagerduty.pagerduty.pagerduty_enrich")

_API_BASE = "https://api.pagerduty.com"

_VALID_INCLUDES = frozenset(
    {"alerts", "log_entries", "notes", "service_details", "on_calls"}
)


def _headers(api_token: str) -> dict[str, str]:
    """Build standard PagerDuty API request headers."""
    return {
        "Authorization": f"Token token={api_token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.pagerduty+json;version=2",
    }


def _get_json(url: str, api_token: str, params: dict | None = None) -> dict:
    """Perform a GET request and return the JSON body, or empty dict on error."""
    try:
        resp = requests.get(url, headers=_headers(api_token), params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.error("PagerDuty API error for %s: %s", url, exc)
        return {}


def _fetch_alerts(incident_id: str, api_token: str) -> list[dict]:
    """Fetch alerts associated with an incident."""
    data = _get_json(f"{_API_BASE}/incidents/{incident_id}/alerts", api_token)
    return data.get("alerts", [])


def _fetch_log_entries(incident_id: str, api_token: str) -> list[dict]:
    """Fetch log entries / timeline for an incident."""
    data = _get_json(f"{_API_BASE}/incidents/{incident_id}/log_entries", api_token)
    return data.get("log_entries", [])


def _fetch_notes(incident_id: str, api_token: str) -> list[dict]:
    """Fetch notes attached to an incident."""
    data = _get_json(f"{_API_BASE}/incidents/{incident_id}/notes", api_token)
    return data.get("notes", [])


def _fetch_service_details(service_id: str, api_token: str) -> dict:
    """Fetch the full service object."""
    if not service_id:
        return {}
    data = _get_json(f"{_API_BASE}/services/{service_id}", api_token)
    return data.get("service", {})


def _fetch_on_calls(service_id: str, api_token: str) -> list[dict]:
    """Fetch the current on-call entries for a service's escalation policy."""
    if not service_id:
        return []
    # First get the escalation policy ID from the service
    svc = _get_json(f"{_API_BASE}/services/{service_id}", api_token)
    ep_id = svc.get("service", {}).get("escalation_policy", {}).get("id")
    if not ep_id:
        return []

    data = _get_json(
        f"{_API_BASE}/oncalls",
        api_token,
        params={"escalation_policy_ids[]": ep_id},
    )
    return data.get("oncalls", [])


def main(event: dict[str, Any], **kwargs) -> dict[str, Any]:
    """EDA event filter entry point.

    Enriches the event with additional PagerDuty context based on the
    ``include`` parameter list.  Returns the event with new keys added
    under an ``enrichment`` sub-dictionary.

    If required fields (``incident_id``, ``api_token``) are missing the
    event is returned unmodified.
    """
    api_token = kwargs.get("api_token", "")
    include = kwargs.get("include", [])

    if not api_token:
        logger.warning("No api_token provided — skipping enrichment")
        return event

    incident_id = event.get("incident_id", "")
    service_id = event.get("service_id", "")

    if not incident_id:
        logger.debug("No incident_id in event — skipping enrichment")
        return event

    if not re.match(r'^[A-Z0-9]+$', incident_id):
        logger.warning("Invalid incident_id format: %s — skipping enrichment", incident_id)
        return event

    invalid = set(include) - _VALID_INCLUDES
    if invalid:
        logger.warning("Ignoring unknown enrichment types: %s", invalid)

    enrichment: dict[str, Any] = {}

    if "alerts" in include:
        enrichment["alerts"] = _fetch_alerts(incident_id, api_token)

    if "log_entries" in include:
        enrichment["log_entries"] = _fetch_log_entries(incident_id, api_token)

    if "notes" in include:
        enrichment["notes"] = _fetch_notes(incident_id, api_token)

    if "service_details" in include:
        enrichment["service_details"] = _fetch_service_details(service_id, api_token)

    if "on_calls" in include:
        enrichment["on_calls"] = _fetch_on_calls(service_id, api_token)

    event["enrichment"] = enrichment
    logger.info(
        "Enriched incident %s with: %s",
        incident_id,
        ", ".join(enrichment.keys()),
    )
    return event
