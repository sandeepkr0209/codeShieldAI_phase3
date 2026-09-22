---
title: Security Misconfiguration
category: Configuration
cwe: CWE-16
owasp: A05:2021 - Security Misconfiguration
---

# Security Misconfiguration

Security misconfiguration covers a broad class of issues where an
application, framework, server, or platform is deployed with insecure
default settings, unnecessary features enabled, verbose error output, or
missing hardening — rather than a flaw in custom application logic itself.

## Common forms

- Debug mode or verbose stack traces enabled in production, leaking
  internal paths, framework versions, or even source code.
- Default credentials or sample/admin accounts left active.
- Unnecessary services, ports, or admin interfaces exposed to the
  internet.
- Overly permissive CORS configuration (e.g. reflecting any Origin with
  credentials allowed).
- Missing security headers (Content-Security-Policy,
  X-Content-Type-Options, Strict-Transport-Security, etc.).
- Cloud storage buckets or database instances left publicly accessible.

## Why it matters

These issues are often trivial for an attacker to find via automated
scanning, and they frequently provide either direct access to sensitive
data or valuable reconnaissance information that makes other attacks
easier.

## Remediation

- Disable debug/verbose error modes in production; return generic error
  responses to clients while logging full details server-side only.
- Remove or disable default accounts, sample applications, and unused
  features/services.
- Apply a minimal, explicit CORS policy rather than a permissive default.
- Set standard security headers on all HTTP responses.
- Regularly review cloud/infrastructure configuration against a hardening
  checklist rather than relying on defaults.
