# Contributing to pagerduty.pagerduty

Thank you for your interest in contributing to the PagerDuty Ansible
collection. This document explains the process for contributing code,
reporting issues, and running tests.

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | >= 3.12 |
| ansible-core | >= 2.16 |
| pytest | latest |

### Environment Setup

1. Fork the repository and clone your fork:

   ```bash
   mkdir -p ansible_collections/pagerduty
   git clone https://github.com/<your-fork>/pagerduty.pagerduty.git ansible_collections/pagerduty/pagerduty
   cd ansible_collections/pagerduty/pagerduty
   ```

2. Create a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install ansible-core>=2.16 ansible-lint yamllint flake8 pytest pytest-cov
   ```

3. Set your PagerDuty API token (for integration tests):

   ```bash
   export PAGERDUTY_API_TOKEN="your-api-token"
   ```

## Running Tests

```bash
make lint         # yamllint + flake8 + ansible-lint
make sanity       # ansible-test sanity checks
make unit         # pytest unit tests
make integration  # ansible-test integration (requires API token)
make test         # lint + sanity + unit
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run `make test` and ensure all checks pass
4. Add a changelog fragment in `changelogs/fragments/`
5. Submit a PR with a conventional commit title (e.g., `feat: add new module`)

### PR Title Format

Titles must follow conventional commit format (max 72 characters):

```
type(scope): description
```

Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`

### Changelog Fragments

Add a YAML file in `changelogs/fragments/` with a descriptive name:

```yaml
# changelogs/fragments/add-status-page-module.yml
minor_changes:
  - Added status_page module for managing PagerDuty status pages.
```

## Module Development

All modules should:

- Import from `plugins.module_utils.pagerduty`
- Include DOCUMENTATION, EXAMPLES, and RETURN docstrings
- Support `check_mode`
- Use the `state=present/absent` pattern for CRUD modules
- Handle PagerDutyError exceptions

## Code Style

- Python: flake8 with max-line-length=120
- YAML: yamllint with max line length 160
- Roles: use FQCN for all module references

## License

By contributing, you agree that your contributions will be licensed
under GPL-3.0-or-later.
