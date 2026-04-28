# Orthodox Connect Backup and Restore Design

## 1. Backup Goals

Backups should let trusted operators recover Orthodox Connect without weakening the invite-only and role-based trust model.

Goals:

- Preserve portal identity, groups, roles, invites, verification records, rooms, meetings, and audit events.
- Preserve Prosody data and configuration needed for XMPP service recovery.
- Preserve Jitsi configuration needed for authenticated meeting recovery.
- Preserve reverse proxy configuration and Caddy-managed runtime data where needed for TLS recovery.
- Keep backup output local for this stage.
- Keep real secrets out of Git.
- Keep backup manifests useful without exposing passwords, raw tokens, JWT bodies, session cookies, or `.env` contents.
- Support test restores before production depends on a backup set.
- Make backup contents clear enough that an operator can verify what was captured.

Backups are sensitive community records and should be handled with the same care as the live server.

## 2. Restore Goals

Restores should recover trusted service state in a controlled order.

Goals:

- Restore portal trust data before chat, meetings, or user access resumes.
- Confirm public registration remains disabled after restore.
- Confirm open federation remains disabled after restore.
- Confirm Jitsi meeting creation remains authenticated and role-gated.
- Restore only from backup sets that match the intended environment.
- Fail closed if required data, secrets, or configuration are missing.
- Preserve audit records and operator notes for review.
- Avoid using staging or local data to repair production.
- Avoid deleting current data before a restore target has been reviewed.

If portal identity data cannot be trusted, operators should keep chat and meetings offline until roles, room access, suspension state, and audit records are reviewed.

## 3. Backup Scope

### Portal Database

The portal PostgreSQL database is the highest-priority backup target.

Back up:

- `users`
- `groups`
- `group_memberships`
- `roles`
- `user_roles`
- `invites`
- `verification_requests`
- `verification_decisions`
- `rooms`
- `room_memberships`
- `meetings`
- `meeting_guests`
- `meeting_token_issuances`
- `audit_events`
- Migration state, if tracked by the database.

Use a PostgreSQL logical dump so the data can be restored into a clean PostgreSQL volume.

### Portal Uploaded Files If Present

Portal uploads are not part of the current MVP workflow, but the backup design should reserve space for them.

If portal uploads are added later, back up:

- Uploaded files.
- Upload metadata.
- Access policy tied to each file.
- Any thumbnails or generated files needed to serve the upload.

Do not commit uploaded files to Git.

### Prosody Data

Back up the Prosody data volume.

This may include:

- Local XMPP account state.
- MUC room state.
- Message archive data if enabled.
- Prosody runtime data and keys stored in the data volume.

Prosody data can reveal sensitive account, room, and message metadata.

### Prosody Config

Back up committed Prosody configuration and any operator-controlled deployment copy.

Include:

- `prosody/`
- The expected XMPP domain variables from environment templates.
- Notes needed to confirm registration and federation remain disabled.

Do not store real XMPP passwords or secret values in repository documentation.

### Jitsi Config

Back up Jitsi configuration and runtime data needed for authenticated meeting service.

Include:

- Jitsi web configuration volume.
- Jitsi Prosody configuration volume.
- Jicofo configuration volume.
- JVB configuration volume.
- Jitsi config files under `jitsi/` where present.

JWT secrets must come from operator secret storage, not from committed files.

### Reverse Proxy Config

Back up reverse proxy configuration and Caddy-managed runtime data where needed.

Include:

- `reverse-proxy/`
- Caddy runtime config volume, if present.
- Caddy data volume containing ACME account and certificate state, if managed by the stack.

Caddy data can contain TLS private material and must be treated as sensitive.

### Environment Templates

Back up environment templates from the repository.

Include:

- `.env.example`
- Documentation describing required variables.

Do not treat `.env.example` as a secret source. Real `.env` files should be backed up only through operator-controlled secret storage outside Git.

### Documentation

Back up documentation needed to operate and restore the system.

Include:

- `README.md`
- `docs/`
- Backup manifests.
- Operator runbooks if they are safe to include and contain no real secrets.

The Git repository should normally be the source for documentation, but a backup set may include a snapshot to document exactly what guidance matched the backup.

## 4. Data Not Backed Up

Do not include by default:

- Docker images.
- Docker build caches.
- Package manager caches.
- Temporary files.
- Routine container logs.
- Debug logs.
- Local development data.
- Staging data inside production backups.
- Production data inside local or staging backups.
- Real `.env` files in Git-tracked backup snapshots.
- Raw invite tokens.
- Recovery tokens.
- Jitsi JWT token bodies.
- Session cookies.
- Passwords.
- Message bodies copied into logs or manifests.
- Remote backup provider state, because remote backups are not part of this stage.

Incident logs may be preserved separately by an operator when needed, but routine logs should not be part of normal backups.

## 5. Backup Directory Structure

Local backups should use a predictable directory layout.

Recommended structure:

```text
backups/
	YYYYMMDD-HHMMSS_environment_host/
		manifest.txt
		checksums.txt
		portal/
			postgres.sql
			uploads/
		prosody/
			data/
			config/
		jitsi/
			config/
		reverse-proxy/
			config/
			data/
		repository/
			env.example
			docs/
```

Rules:

- Backup output must stay out of Git.
- Each backup set should be self-contained enough to identify source environment, timestamp, and included components.
- The manifest must not include secret values.
- Empty placeholder directories may be omitted when the related feature is not present.

## 6. Backup Naming Format

Use UTC timestamps and environment labels.

Recommended format:

```text
YYYYMMDD-HHMMSS_environment_host
```

Example shape:

```text
20260427-181530_production_primary
```

Naming rules:

- Use UTC time.
- Include the environment.
- Include a non-secret host label.
- Do not include real domains if the backup name will be shared.
- Do not include usernames, parish names, invite tokens, meeting names, or secret identifiers.
- If archives are created later, keep the directory name as the archive base name.

## 7. Backup Frequency

Frequency depends on environment and data value.

Recommended production frequency:

- Database backup daily.
- Configuration backup daily or after configuration changes.
- Full local backup at least weekly.
- Manual backup before migrations, upgrades, Jitsi changes, Prosody changes, reverse proxy changes, or restore testing.
- Backup verification after any backup script or volume layout change.

Recommended staging frequency:

- Before persistence tests.
- Before restore tests.
- Before production-like deployment rehearsals.

Recommended local development frequency:

- Optional, because local data should be disposable and fake.

## 8. Retention Policy

Retention should balance recovery needs, disk capacity, and privacy.

Suggested starting point for production:

- Daily backups for 7 to 14 days.
- Weekly backups for 4 to 8 weeks.
- Monthly backups for 3 to 12 months if the operator has enough storage and a reason to keep them.
- Pre-upgrade backups until the upgrade is accepted and a newer tested backup exists.
- Incident-related backups until review is complete.

Retention rules:

- Delete expired backups through an operator-reviewed process.
- Do not delete the only known-good backup.
- Do not keep backups longer than the deployment can justify.
- Treat deleted-account data inside old backups per the documented retention policy.
- Keep backup storage usage monitored so backups do not fill the host disk.

## 9. Local Backup Workflow

The local backup workflow should be simple and repeatable.

Workflow:

1. Load environment settings from `.env` or the operator-provided environment.
2. Confirm the target backup path is outside Git-tracked output.
3. Create a timestamped backup directory.
4. Write a manifest with timestamp, environment, source commit, and included components.
5. Dump PostgreSQL to the portal backup directory.
6. Copy Prosody data and config.
7. Copy Jitsi config and runtime data if present.
8. Copy reverse proxy config and Caddy data if present.
9. Copy `.env.example` and documentation snapshot.
10. Write checksums if checksum support is enabled.
11. Verify required files exist and are non-empty where expected.
12. Print the backup location without printing secret values.

The workflow must not print `.env` contents, database passwords, JWT secrets, raw invite tokens, session cookies, or TLS private keys.

## 10. Future Remote Backup Workflow Placeholder

Remote backups are future scope and must not be added in this stage.

Before remote backups are implemented, the project should define:

- Whether backups are encrypted before leaving the host.
- Who controls the encryption keys.
- Which remote provider or storage location is acceptable.
- How restore is tested from remote storage.
- How remote retention works.
- How operators revoke access after compromise.
- How backup transfer logs avoid secret leakage.
- How production backups are kept out of local and staging environments.

Remote backup providers should not be configured until a separate reviewed implementation pass approves them.

## 11. Restore Order

Restore order should recover the source of trust before dependent services.

Recommended order:

1. Prepare a replacement host or clean restore target.
2. Restore the repository checkout from Git.
3. Restore `.env` from operator-controlled secret storage.
4. Restore Docker volumes or backup directories.
5. Restore the PostgreSQL logical dump.
6. Start PostgreSQL only.
7. Run portal migration or schema checks if required.
8. Start the portal and confirm admin access.
9. Review users, roles, invites, verification records, rooms, meetings, suspension state, and audit events.
10. Start the reverse proxy.
11. Start Prosody and confirm browser transports.
12. Start Converse.js.
13. Start Jitsi components.
14. Issue a test meeting token with fake or approved test data.
15. Confirm public registration remains disabled.
16. Confirm federation remains disabled unless a later approved policy enabled it.
17. Confirm Jitsi authentication remains enabled.
18. Notify users only after administrator review is complete.

If any required secret is suspected to be exposed, rotate it before restoring public access.

## 12. Restore Safety Checks

Restores should include explicit safety checks before data is written.

Required checks:

- Confirm the restore target environment.
- Confirm the backup environment matches the restore target.
- Confirm the backup manifest exists.
- Confirm the backup timestamp is the intended restore point.
- Confirm the current restore target has been preserved or is disposable.
- Confirm enough disk space exists.
- Confirm `.env` is present through operator secret storage.
- Confirm required secrets are not placeholders in production.
- Confirm public registration remains disabled.
- Confirm open federation remains disabled.
- Confirm Jitsi JWT authentication remains enabled.
- Confirm Jitsi guests and public room creation match MVP policy.
- Confirm PostgreSQL restore target is clean or intentionally overwritten.
- Confirm Prosody and Jitsi services are stopped before restoring their data.
- Confirm no production backup is being restored into casual local development.

If checks fail, stop the restore and preserve the current state for review.

## 13. Test Restore Procedure

Test restores should use disposable data unless the operator has approved a controlled sensitive restore target.

Procedure:

1. Create or select a backup set.
2. Prepare a clean test environment.
3. Restore repository files and environment variables for the test environment.
4. Restore PostgreSQL.
5. Start PostgreSQL and portal checks.
6. Confirm portal admin workflows load.
7. Confirm fake users, roles, invites, verification requests, rooms, meetings, and audit events are present.
8. Restore Prosody data and config.
9. Confirm browser XMPP transport paths work.
10. Restore reverse proxy data and config if included in the test.
11. Restore Jitsi config.
12. Confirm Jitsi requires valid JWT access.
13. Confirm backup manifests and checksums match expectations.
14. Record test date, backup timestamp, restore target, checks passed, failures, and operator.

Production restore tests should be scheduled and reviewed before relying on the backup process.

## 14. Backup Verification Checks

Each backup should be checked before it is considered usable.

Verification checks:

- Backup directory exists.
- Manifest exists.
- Manifest has timestamp, environment, source host label, and source commit where available.
- PostgreSQL dump exists and is non-empty.
- Prosody data or explicit omission is recorded.
- Prosody config exists.
- Jitsi config or explicit omission is recorded.
- Reverse proxy config exists.
- Caddy data exists if Caddy-managed TLS data is included.
- `.env.example` is included.
- Documentation snapshot is included or Git commit is recorded.
- Checksums exist if checksum support is enabled.
- Backup output is outside Git.
- Backup manifest does not contain raw secrets.
- Backup listing command can find the backup.
- A recent restore test has passed for the relevant environment.

Verification should fail closed. A partial backup should be marked partial and should not replace the last known-good backup.

## 15. Failure Scenarios

Operators should plan for common backup and restore failures.

| Failure Scenario | Expected Response |
| ---------------- | ----------------- |
| PostgreSQL dump fails | Mark backup failed, keep previous known-good backup, inspect database and disk state. |
| Disk fills during backup | Stop backup, free safe space, review retention, rerun after capacity is available. |
| Prosody data copy fails | Mark backup partial and avoid replacing a complete backup. |
| Jitsi config copy fails | Mark backup partial and record which Jitsi components were missing. |
| Reverse proxy data copy fails | Mark TLS recovery risk and keep service routes unchanged until reviewed. |
| Manifest contains sensitive values | Remove or quarantine the backup, rotate exposed secrets if needed, fix manifest generation. |
| Backup archive is corrupted | Keep previous backup, rerun backup, test restore before deleting older backups. |
| Wrong environment selected | Stop immediately, preserve current state, do not continue restore. |
| Restore target has existing data | Preserve or snapshot current data before overwrite, unless target is disposable. |
| PostgreSQL restore fails | Stop dependent services, inspect dump and target version, restore to disposable target first. |
| Prosody starts with registration enabled | Stop Prosody, correct environment or config, confirm no public registration occurred. |
| Jitsi allows public room creation | Stop Jitsi public route, correct JWT and guest settings, review logs. |
| Caddy certificate data missing | Reissue through normal Caddy ACME flow after DNS and public ports are verified. |
| Secret exposure suspected | Rotate affected secrets before public service resumes. |

Failure handling should preserve evidence and avoid widening access.

## 16. Rollback Plan

Backup and restore rollback should return the system to the last known-good state without deleting evidence.

Rollback steps:

1. Stop affected public routes or services if restored state is unsafe.
2. Preserve current data, failed restore output, manifests, and relevant logs for review.
3. Identify the last known-good backup and configuration.
4. Restore only the affected component when that is safe.
5. Restore the full stack only if component rollback cannot preserve trust state.
6. Confirm portal admin access works.
7. Confirm users, roles, verification records, rooms, meetings, suspension state, and audit events match expectations.
8. Confirm public registration remains disabled.
9. Confirm federation remains disabled.
10. Confirm Jitsi authentication remains enabled.
11. Rotate any secret that may have been exposed.
12. Record the rollback result in operator notes or portal audit records where supported.

Rollback must not delete portal users, roles, groups, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration unless a separate reviewed data repair or retention process explicitly requires it.
