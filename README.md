# PagerDuty Ansible Collection

[![CI](https://github.com/ansible-collections/pagerduty.pagerduty/actions/workflows/ci.yml/badge.svg)](https://github.com/ansible-collections/pagerduty.pagerduty/actions/workflows/ci.yml)

Ansible Collection for managing PagerDuty resources, incidents, and event-driven automation. Provides 50 modules, 5 EDA plugins, and 6 roles.

## Requirements

| Dependency | Version |
|---|---|
| Python | >= 3.12 |
| ansible-core | >= 2.16.0 |

## Installation

```bash
ansible-galaxy collection install pagerduty.pagerduty
```

## Authentication

Set your PagerDuty API token via:
1. **Module parameter**: `api_token: "your-token"`
2. **Environment variable**: `PAGERDUTY_API_TOKEN` or `PD_API_TOKEN`

## Modules

### State Modules (30)

| Module | Description |
|---|---|
| `pagerduty.pagerduty.automation_action` | Manage PagerDuty automation actions |
| `pagerduty.pagerduty.automation_action_runner` | Manage PagerDuty automation action runners |
| `pagerduty.pagerduty.business_service` | Manage PagerDuty business services |
| `pagerduty.pagerduty.escalation_policy` | Manage PagerDuty escalation policies |
| `pagerduty.pagerduty.event_orchestration` | Manage PagerDuty event orchestrations |
| `pagerduty.pagerduty.event_orchestration_global_rule` | Manage PagerDuty event orchestration global rules |
| `pagerduty.pagerduty.event_orchestration_integration` | Manage PagerDuty event orchestration integrations |
| `pagerduty.pagerduty.event_orchestration_router` | Manage PagerDuty event orchestration router rules |
| `pagerduty.pagerduty.event_orchestration_service_rule` | Manage PagerDuty service-level event orchestration rules |
| `pagerduty.pagerduty.extension` | Manage PagerDuty extensions |
| `pagerduty.pagerduty.incident` | Manage PagerDuty incidents |
| `pagerduty.pagerduty.incident_custom_field` | Manage PagerDuty incident custom fields |
| `pagerduty.pagerduty.incident_note` | Add notes to PagerDuty incidents |
| `pagerduty.pagerduty.incident_workflow` | Manage PagerDuty incident workflows |
| `pagerduty.pagerduty.incident_workflow_trigger` | Manage PagerDuty incident workflow triggers |
| `pagerduty.pagerduty.maintenance_window` | Manage PagerDuty maintenance windows |
| `pagerduty.pagerduty.response_play` | Manage PagerDuty response plays |
| `pagerduty.pagerduty.schedule` | Manage PagerDuty on-call schedules |
| `pagerduty.pagerduty.schedule_override` | Manage PagerDuty schedule overrides |
| `pagerduty.pagerduty.service` | Manage PagerDuty services |
| `pagerduty.pagerduty.service_dependency` | Manage PagerDuty service dependencies |
| `pagerduty.pagerduty.service_integration` | Manage PagerDuty service integrations |
| `pagerduty.pagerduty.tag` | Manage PagerDuty tags |
| `pagerduty.pagerduty.tag_assignment` | Assign or remove PagerDuty tags from entities |
| `pagerduty.pagerduty.team` | Manage PagerDuty teams |
| `pagerduty.pagerduty.team_membership` | Manage PagerDuty team membership |
| `pagerduty.pagerduty.user` | Manage PagerDuty users |
| `pagerduty.pagerduty.user_contact_method` | Manage PagerDuty user contact methods |
| `pagerduty.pagerduty.user_notification_rule` | Manage PagerDuty user notification rules |
| `pagerduty.pagerduty.webhook_subscription` | Manage PagerDuty V3 webhook subscriptions |

### Info Modules (18)

| Module | Description |
|---|---|
| `pagerduty.pagerduty.ability_info` | List PagerDuty account abilities |
| `pagerduty.pagerduty.analytics_info` | Get PagerDuty analytics data |
| `pagerduty.pagerduty.audit_record_info` | Get PagerDuty audit records |
| `pagerduty.pagerduty.business_service_info` | List or get PagerDuty business services |
| `pagerduty.pagerduty.escalation_policy_info` | List or get PagerDuty escalation policies |
| `pagerduty.pagerduty.event_orchestration_info` | List or get PagerDuty event orchestrations |
| `pagerduty.pagerduty.incident_custom_field_info` | List PagerDuty incident custom fields |
| `pagerduty.pagerduty.incident_info` | List or get PagerDuty incidents |
| `pagerduty.pagerduty.log_entry_info` | Get PagerDuty log entries |
| `pagerduty.pagerduty.notification_info` | List PagerDuty notifications |
| `pagerduty.pagerduty.on_call_info` | Get current PagerDuty on-call entries |
| `pagerduty.pagerduty.priority_info` | List PagerDuty priorities |
| `pagerduty.pagerduty.schedule_info` | List or get PagerDuty schedules |
| `pagerduty.pagerduty.service_info` | List or get PagerDuty services |
| `pagerduty.pagerduty.tag_info` | List PagerDuty tags or get entity tags |
| `pagerduty.pagerduty.team_info` | List or get PagerDuty teams |
| `pagerduty.pagerduty.user_info` | List or get PagerDuty users |
| `pagerduty.pagerduty.vendor_info` | List PagerDuty vendors |

### Event Modules (2)

| Module | Description |
|---|---|
| `pagerduty.pagerduty.event` | Send PagerDuty events via Events API v2 |
| `pagerduty.pagerduty.change_event` | Send PagerDuty change events |

## EDA Plugins

### Source Plugins (2)

| Plugin | Description |
|---|---|
| `pagerduty.pagerduty.pagerduty_webhook` | Receive PagerDuty V3 webhook events via async HTTP server with HMAC-SHA256 validation |
| `pagerduty.pagerduty.pagerduty_api` | Poll PagerDuty REST API for incidents and changes on a configurable interval |

### Event Filters (3)

| Plugin | Description |
|---|---|
| `pagerduty.pagerduty.pagerduty_normalize` | Normalize nested PagerDuty webhook payloads into flat event fields |
| `pagerduty.pagerduty.pagerduty_enrich` | Enrich PagerDuty events with service, team, and escalation policy details |
| `pagerduty.pagerduty.incident_dedup` | Deduplicate PagerDuty incident events by dedup key and time window |

## Roles

| Role | Description |
|---|---|
| `pagerduty.pagerduty.setup` | Bootstrap a PagerDuty organization with teams, users, contact methods, notification rules, and escalation policies |
| `pagerduty.pagerduty.service_onboard` | Onboard a new PagerDuty service end-to-end with schedule, escalation policy, integration, and tags |
| `pagerduty.pagerduty.eda_setup` | Deploy EDA rulebook and PagerDuty webhook subscription for event-driven incident automation |
| `pagerduty.pagerduty.incident_response` | Automated incident response workflow with acknowledge, diagnostics, notes, and resolution |
| `pagerduty.pagerduty.maintenance` | Manage PagerDuty maintenance windows - create and end maintenance periods for services |
| `pagerduty.pagerduty.migration` | Migrate from legacy PagerDuty rulesets to event orchestration with audit and conversion workflows |

## Quick Start Examples

### Create a service with escalation policy

```yaml
- name: Onboard production API service
  hosts: localhost
  connection: local
  tasks:
    - name: Create escalation policy
      pagerduty.pagerduty.escalation_policy:
        name: API Team Escalation
        escalation_rules:
          - escalation_delay_in_minutes: 10
            targets:
              - type: schedule_reference
                id: "{{ schedule_id }}"
        state: present
      register: ep

    - name: Create service
      pagerduty.pagerduty.service:
        name: Production API
        description: Core production API service
        escalation_policy_id: "{{ ep.policy.id }}"
        alert_creation: create_alerts_and_incidents
        state: present
```

### Auto-remediation with EDA

```yaml
---
- name: PagerDuty auto-remediation
  hosts: all
  sources:
    - pagerduty.pagerduty.pagerduty_webhook:
        host: 0.0.0.0
        port: 5000
        token: "{{ WEBHOOK_SECRET }}"
  rules:
    - name: Restart service on high CPU alert
      condition: event.event_type == "incident.triggered" and "high_cpu" in event.summary
      action:
        run_playbook:
          name: remediate_high_cpu.yml
```

## Testing

```bash
make lint    # yamllint + flake8 + ansible-lint
make sanity  # ansible-test sanity
make unit    # pytest unit tests
make test    # all of the above
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

GPL-3.0-or-later
