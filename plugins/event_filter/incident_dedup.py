"""
incident_dedup.py - EDA event filter that deduplicates rapid-fire webhook deliveries.

PagerDuty may deliver the same webhook event multiple times in quick succession
(retries, multiple subscriptions, or V3 webhook fanout).  This filter maintains
a time-windowed cache of recently processed event keys and drops duplicates
that arrive within the configured window.

Arguments:
    window_seconds:  Duration in seconds to remember an event key (default: 10)
    key_fields:      List of event field names whose combined value forms the
                     deduplication key (default: ["incident_id", "event_type"])

Example rulebook usage:
    filters:
      - pagerduty.pagerduty.incident_dedup:
          window_seconds: 15
          key_fields:
            - incident_id
            - event_type
"""

import logging
import time
from typing import Any

logger = logging.getLogger("pagerduty.pagerduty.incident_dedup")

# Module-level cache shared across invocations within the same EDA process.
# Structure: { composite_key: expiry_timestamp }
_seen_cache: dict[str, float] = {}


def _build_key(event: dict, key_fields: list[str]) -> str:
    """Build a composite deduplication key from the specified event fields."""
    parts = []
    for field in key_fields:
        value = event.get(field, "")
        parts.append(str(value))
    return "|".join(parts)


def _prune_expired(now: float) -> None:
    """Remove cache entries whose expiry time has passed."""
    expired = [k for k, expiry in _seen_cache.items() if expiry <= now]
    for k in expired:
        del _seen_cache[k]


def main(event: dict[str, Any], **kwargs) -> dict[str, Any] | None:
    """EDA event filter entry point.

    Returns the event unchanged if it has not been seen within the
    deduplication window.  Returns ``None`` (drop) if a duplicate
    key is found in the cache.

    Args:
        event:  The EDA event dictionary.
        **kwargs:  Filter arguments from the rulebook.

    Returns:
        The event dict to continue processing, or None to drop it.
    """
    window_seconds = int(kwargs.get("window_seconds", 10))
    key_fields = kwargs.get("key_fields", ["incident_id", "event_type"])

    now = time.monotonic()

    # Periodically prune to keep memory bounded
    _prune_expired(now)

    composite_key = _build_key(event, key_fields)

    if not composite_key or composite_key == "|".join([""] * len(key_fields)):
        # If all key fields are empty we cannot deduplicate — pass through
        logger.debug("Dedup key fields are empty — passing event through")
        return event

    if composite_key in _seen_cache:
        remaining = _seen_cache[composite_key] - now
        logger.info(
            "Dropping duplicate event (key=%s, window expires in %.1fs)",
            composite_key,
            max(remaining, 0),
        )
        return None

    _seen_cache[composite_key] = now + window_seconds
    logger.debug(
        "Recorded event key=%s (expires in %ds)",
        composite_key,
        window_seconds,
    )
    return event
