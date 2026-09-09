# MVP Readiness - Si Sebel

## Status

**Controlled pilot ready, not yet production-ready for public school deployment.**

The local MVP flow is covered by automated tests, but a production launch still
requires school approval, current knowledge-base verification, and a real
WhatsApp staging test.

## Verified locally

- Database migration and seeded SQLite knowledge base.
- Menu commands 1-6 through `MessageProcessor`.
- School information, jurusan (including TKJ alias), PPDB, calendar, contact,
  facilities, extracurricular, FAQ, and unknown-intent responses.
- Empty and malicious input handling.
- Intent collision cases such as `jadwal ujian` and `kontak sekolah`.
- Persistent message-id idempotency and database backup integrity.
- Formatting, type/compile checks, lock validation, restore smoke test, and
  dependency security scan.

The end-to-end seeded flow is implemented in
`tests/test_mvp_end_to_end.py`. The test count and coverage shown in CI are the
source of truth; documentation test cases are not evidence of execution.

## Release gates still pending

### School and data acceptance

- Obtain written approval from SMKN 11 Jakarta for every active record.
- Replace placeholder or unverified records with current official sources.
- Confirm PPDB schedule, academic calendar, contacts, facilities, and
  extracurricular data for the target school year.
- Record the real verification date instead of treating seed execution time as
  `verified_at`.

### WhatsApp and operations

- Run an end-to-end test with a WhatsApp provider staging credential.
- Verify webhook signature, retries, timeout behavior, duplicate delivery, and
  provider outage handling in the deployed environment.
- Perform a Docker deployment smoke test on the target host.
- Configure monitoring, alerting, scheduled backups, restore drills, and
  rollback ownership.
- Complete manual acceptance testing with school staff.

## Go-live decision

Do not label this release production-ready until every pending gate above has
an owner, evidence, and a recorded pass result. Until then, use the bot only
for a controlled pilot with an explicit escalation path to school staff.
