===========================
Collection Release Notes
===========================

.. contents:: Topics

v0.2.0
======

Release Summary
---------------

Bug fix and documentation quality release.

Bugfixes
--------

- Fix escalation_policy delete using wrong API path (``/teams/...`` → ``/escalation_policies/{id}``).
- Fix all modules using unpaginated list+filter in get_current_state; now uses direct ``GET /resource/{id}``.
- Fix incident module requiring both ``incident`` and ``incidents`` params simultaneously.
- Fix silent swallowing of all ClientError exceptions; now only swallows 404.
- Fix conftest mock using ``client.POST`` (uppercase) instead of ``client.post``.
- Add ``api_key`` validation in Client for clear error on missing credentials.

Documentation
-------------

- Fix galaxy.yml repository URL, README install namespace, and README param name.
- Fix ``version_added`` from ``1.0.0`` to ``0.1.0`` across all modules.
- Fix user module ``short_description`` from "Manage teams" to "Manage users".
- Add real DOCUMENTATION and RETURN descriptions for all modules and parameters.

Improvements
------------

- Add ``required_if`` constraints to all modules.
- Fix ``escalation_policys`` typo to ``escalation_policies`` in info module.
- Change info module pagination params to PagerDuty-native ``offset``/``limit``.
- Add missing ``test_user.py`` and ``test_webhook_subscription.py`` unit tests.
- Add ``Client.get_single()`` method for single-resource retrieval.

v0.1.0
======

Release Summary
---------------

Initial pre-release.
