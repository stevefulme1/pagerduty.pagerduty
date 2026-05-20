# Ansible Collection - stevefulme1.pagerduty

Ansible collection for the PagerDuty API, auto-generated from the official OpenAPI specification.

## Modules

| Module | Description |
|--------|-------------|
| `escalation_policy` | Manage escalation policies |
| `incident` | Manage incidents |
| `maintenance_window` | Manage maintenance windows |
| `schedule` | Manage schedules |
| `service` | Manage services |
| `team` | Manage teams |
| `user` | Manage users |
| `webhook_subscription` | Manage webhook subscriptions |

Each module has a corresponding `_info` module for read-only queries.

## Installation

```bash
ansible-galaxy collection install stevefulme1.pagerduty
```

## Authentication

All modules require `api_url` and `api_token` parameters, or the equivalent environment variables.

## License

GPL-3.0-or-later
