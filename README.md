# Ansible Collection - pagerduty.pagerduty

Ansible collection for the PagerDuty API, auto-generated from the official OpenAPI specification.

## Modules

| Module | Description |
|--------|-------------|
| `escalation_policy` | Manage escalation policies |
| `escalation_policy_info` | Retrieve escalation policy information |
| `incident` | Manage incidents |
| `incident_info` | Retrieve incident information |
| `maintenance_window` | Manage maintenance windows |
| `maintenance_window_info` | Retrieve maintenance window information |
| `schedule` | Manage schedules |
| `schedule_info` | Retrieve schedule information |
| `service` | Manage services |
| `service_info` | Retrieve service information |
| `team` | Manage teams |
| `team_info` | Retrieve team information |
| `user` | Manage users |
| `user_info` | Retrieve user information |
| `webhook_subscription` | Manage webhook subscriptions |
| `webhook_subscription_info` | Retrieve webhook subscription information |

## Installation

```bash
ansible-galaxy collection install pagerduty.pagerduty
```

## Authentication

All modules require an `api_key` parameter, or the `PAGERDUTY_API_KEY` environment variable.
Optionally set `api_url` to override the default PagerDuty API base URL.

## License

GPL-3.0-or-later
