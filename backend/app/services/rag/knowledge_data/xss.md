---
title: Cross-Site Scripting (XSS)
category: Injection
cwe: CWE-79
owasp: A03:2021 - Injection
---

# Cross-Site Scripting (XSS)

Cross-Site Scripting occurs when an application includes untrusted data in a
web page without properly encoding or sanitizing it, allowing an attacker to
inject client-side script that executes in another user's browser session.
This can be used to steal session cookies/tokens, perform actions as the
victim, deface pages, or redirect users to malicious sites.

## Common forms

- **Reflected XSS** — untrusted input from the current request (e.g. a
  query parameter) is echoed back into the page's HTML without encoding.
- **Stored XSS** — untrusted input is saved (e.g. in a comment or profile
  field) and later rendered to other users without encoding.
- **DOM-based XSS** — client-side JavaScript itself writes untrusted data
  into the DOM using unsafe sinks (`innerHTML`, `document.write`, etc.).

## Why it matters

Because the injected script runs in the victim's authenticated browser
context, XSS effectively grants the attacker many of the same capabilities
the victim has within that web application.

## Remediation

- Contextually encode all untrusted output — HTML-encode for HTML body
  content, attribute-encode for attribute values, JS-string-encode for
  inline script contexts, etc.
- Prefer frameworks/templating engines that auto-escape by default, and
  avoid manually opting out (`dangerouslySetInnerHTML`, `v-html`, etc.)
  for untrusted content.
- Set a Content-Security-Policy header to reduce the impact of any XSS
  that does slip through.
- Avoid unsafe DOM sinks with untrusted data; prefer `textContent` over
  `innerHTML` when inserting user-controlled strings.
