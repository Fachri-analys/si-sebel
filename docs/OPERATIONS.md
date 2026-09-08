# Si Sebel Operations Runbook

## Deployment

1. Build the image from the reviewed commit.
2. Configure `config/.env` from the deployment secret store; do not copy it
   into the repository or image.
3. Run `docker compose up -d --build`.
4. Confirm `docker compose ps` reports the bot as healthy.
5. Send a staging WhatsApp test message before enabling production traffic.

## Backup and restore

Create and verify a backup before deployments:

```bash
python scripts/db_admin.py backup --path /app/data/sisebel.db \
  --output /backup/sisebel-$(date +%Y%m%d-%H%M%S).db
python scripts/db_admin.py verify --path /backup/sisebel-latest.db
```

To restore, stop the bot, preserve the current database, replace the database
with a verified backup, and start the bot again. Run the healthcheck and a
read-only FAQ smoke test before accepting traffic. Keep backups on storage
separate from the application host and retain multiple generations.

## Rollback

Deploy the previous known-good image/commit, run the healthcheck, and verify a
staging message. Do not roll back by deleting the database; restore the
database only when corruption or an incompatible migration is confirmed.

## Secret rotation

Rotate the WhatsApp credentials, `PHONE_HASH_KEY`, and Redis credentials in the
secret store. Restart the service, verify health, and remove the old secret
only after the new connection has been tested. Never print secret values in CI
logs.

## Incident response

Disable traffic or stop the bot if it sends incorrect school information,
repeatedly retries provider calls, or loses database integrity. Preserve
sanitized logs and the affected commit, then restore the last verified backup
if required. Provider webhook and credential incidents require staging
verification before production restart.

## Pilot limitations

The repository is suitable for a controlled pilot, not an unconditional
production-ready claim, until provider staging tests, dependency locking,
restore drills, and monitoring/alerting are completed.
