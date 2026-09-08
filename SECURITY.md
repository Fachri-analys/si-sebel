# Security Policy

## Supported versions

Only the latest commit on `main` is actively maintained during the controlled
pilot. Older commits should not be used for deployment.

## Reporting a vulnerability

Please do not open a public issue for a security vulnerability. Report it
privately to the repository owner through GitHub Security Advisories or the
maintainer's verified contact channel. Include:

- a clear description and impact;
- reproducible steps or a minimal proof of concept;
- affected commit, configuration, and environment;
- a suggested mitigation, if known.

Do not include real user data, credentials, provider tokens, or WhatsApp
session files in the report.

## Security expectations

- Secrets must come from the environment or a secret manager.
- Logs must not contain raw phone numbers, message content, or credentials.
- Production changes require tests, review, and a rollback plan.
- Knowledge-base content must be verified before it is activated for users.

