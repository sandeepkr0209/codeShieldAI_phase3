---
title: SQL Injection
category: Injection
cwe: CWE-89
owasp: A03:2021 - Injection
---

# SQL Injection

SQL Injection happens when an application builds a database query by directly
concatenating or interpolating untrusted input (from a user, an API caller, or
any external source) into the query string, instead of treating that input as
data. An attacker who controls part of the query text can change the query's
logic entirely — bypassing authentication checks, reading rows they should
never see, modifying or deleting data, or in some database engines executing
administrative commands.

## How it's typically introduced

- String concatenation or f-strings/format strings used to build SQL text
  (`"SELECT * FROM users WHERE id = " + user_input`)
- ORM "raw query" escape hatches used with untrusted values
- Stored procedures called with untrusted parameters via string building
- Second-order injection, where previously-stored untrusted data is later
  used unsafely to build a new query

## Why it matters

Successful exploitation can expose or corrupt an entire database, and in
some configurations can be used to read files from the server's filesystem
or achieve further compromise of the host.

## Remediation

- Always use parameterized queries / prepared statements, where the query
  structure and the data values are sent to the database separately.
- When using an ORM, prefer its query-builder methods over raw SQL string
  construction; if raw SQL is unavoidable, use the ORM's own parameter
  binding rather than string formatting.
- Apply least-privilege database accounts so that even a successful
  injection has limited blast radius.
- Validate and constrain input where practical (e.g. numeric IDs), but
  treat this as defense-in-depth, not a substitute for parameterization.
