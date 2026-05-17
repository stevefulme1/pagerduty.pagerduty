# Changelog

All notable changes to **stevefulme1.pagerduty** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-05-15

### Added

- Status page, custom field schema, and post-mortem modules
- Pagination parameters to status page and new modules
- Comprehensive unit tests and integration targets for 12 modules
- Pre-commit and linting configuration
- Limit/offset/max_results pagination params to all 19 info modules
- Pagination params to ability, maintenance_window, and priority info modules
- Role README.md files for Galaxy import compliance

### Fixed

- Remove broken test files and pep8 E128 errors
- Resolve pep8 E128 indent and doc-default mismatches
- Add missing role README files
- Resolve Galaxy import validation issues
- Resolve CI failures across lint and sanity
- Change namespace to `stevefulme1` for Galaxy publishing
- Author format and `incident_key` `no_log`
- Sanity `validate-modules` compliance
- Unused format arg in `maintenance_window_info`
- Complete ansible-lint `var-naming` compliance
- Exclude roles from ansible-lint pending param alignment

### Security

- Validate `incident_id` format to prevent SSRF

## [1.0.0] - 2026-05-08

### Added

- Initial release with 50 modules covering services, incidents, teams, users, schedules, escalation policies, event rules, maintenance windows, and more
- 5 EDA event source plugins
- 6 production-ready roles
- CI workflow with lint, sanity, and test jobs
