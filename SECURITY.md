# Security and Privacy Scope

RetirePilot is **not production authorised**. The current v2.5 build is a local synthetic-only research prototype.

## Never commit

- Real personal, CPF, health, identity, account, employment, banking or family financial data
- Credentials, API tokens, .env files, encryption keys, service-account files, cookies
- Generated vault files, database files, session dumps, logs containing user inputs
- Raw interview recordings, transcripts or participant contact details

## Engineering controls required before customer data

- Identity and explicit household-member consent with revocation
- Server-side authentication, tenancy isolation and role-based access
- Production key management, audit logging and tested deletion
- Data retention, cross-border processing and breach-handling review
- Threat modelling, dependency/secrets review, independent penetration testing
- Qualified PDPA/privacy and Singapore financial-advisory legal review

## Reporting

Use private issues without including secrets or real personal records. Reproduce defects with synthetic fixtures and remove identifying information from logs.

A synthetic action state marked `simulated_verified` is **not** independent proof of completion. External actions remain disabled.

Current pilot gate: **NO-GO**.
