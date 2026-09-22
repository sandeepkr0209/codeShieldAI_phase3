---
title: Broken Access Control / IDOR
category: Access Control
cwe: CWE-639
owasp: A01:2021 - Broken Access Control
---

# Broken Access Control / Insecure Direct Object Reference (IDOR)

Broken access control happens when an application fails to properly enforce
what an authenticated (or unauthenticated) user is actually allowed to do or
see. Insecure Direct Object Reference (IDOR) is a specific, very common form:
an endpoint accepts an identifier (e.g. `/api/orders/482`) and returns or
modifies that resource without checking whether the current user actually
owns or is authorized to access it.

## Common forms

- Changing a numeric/UUID identifier in a URL or API request to access
  another user's data.
- Missing server-side authorization checks that rely only on the client
  not exposing a certain UI element ("security through hidden buttons").
- Privilege escalation via parameters the client can freely modify (e.g. a
  `role` or `isAdmin` field trusted from the request body).
- Missing checks on state-changing operations (an attacker directly calls
  an API endpoint the UI would normally guard).

## Why it matters

This is one of the most commonly exploited weaknesses in real-world web
applications precisely because it's easy to introduce (a developer forgets
one ownership check) and easy to discover (an attacker just edits an ID).

## Remediation

- Enforce authorization server-side on every request that reads or
  modifies a resource — verify the authenticated user owns or is
  permitted to act on the specific object requested, not just that they
  are logged in.
- Prefer centralized authorization logic (middleware/decorators) over
  ad-hoc checks scattered through route handlers.
- Deny by default; require an explicit permission check to allow access.
- Use indirect references (e.g. a per-user opaque token) where practical,
  though this is a defense-in-depth measure, not a substitute for a real
  authorization check.
