# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest commit on `main` | ✅ |
| Older commits | ⚠️ Best effort |

## Reporting a Vulnerability

If you discover a security vulnerability:

1. **Do not** open a public GitHub issue.
2. Use GitHub Security Advisories for this repository.
3. If needed, contact the maintainer directly via GitHub.

Given this project handles entitlement and billing-adjacent workflows, responsible disclosure is required.

## What to Include

- Vulnerability description
- Impact and attack scenario
- Steps to reproduce
- Affected endpoints/files
- Proof-of-concept (if available)
- Suggested mitigation (optional)

## Response Timeline Targets

- **Acknowledgement:** within 48 hours
- **Initial triage:** within 7 days
- **Fix timeline:** based on severity and exploitability

## Scope Notes

High-priority findings include:
- Auth bypass in runtime validation
- Seat allocation abuse
- Stripe webhook signature bypass
- Sensitive data exposure in API responses/logs
- Dependency vulnerabilities in production paths
