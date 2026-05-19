===================================
pagerduty.pagerduty Release Notes
===================================

.. contents:: Topics

v1.0.1
======

Security
--------

- Added ``no_log: true`` to API token and webhook secret parameters in all
  role argument specs.
- Changed EDA webhook default bind address from ``0.0.0.0`` to ``127.0.0.1``.
- Created ``argument_specs.yml`` for all roles with sensitive variables.

v1.0.0
======

Major Changes
-------------

- Initial release of the pagerduty.pagerduty collection with 50 modules, 5 EDA plugins, and 6 roles.
