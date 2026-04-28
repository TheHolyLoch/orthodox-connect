# Orthodox Connect Operations Runbook

## 1. Runbook Goals

This runbook defines day-to-day operating procedures for Orthodox Connect.

Goals:

- Keep the stack private, invite-only, and recoverable.
- Give operators repeatable startup, shutdown, restart, health check, log, backup, restore, and incident steps.
- Keep public registration disabled.
- Keep open federation disabled.
- Keep Jitsi room creation authenticated and role-gated.
- Keep PostgreSQL, Prosody internals, Jitsi internals, and Docker administration off public routes.
- Protect `.env`, tokens, logs, backups, and generated service data.
- Preserve portal audit records for trust and access decisions.

This is a design document only. It does not add scripts, change application code, change Docker services, add credentials, or define real hostnames.

## 2. Service Startup Procedure

Startup should bring up the source of trust before dependent services.

Pre-start checks:

1. Confirm the operator is in the repository root.
2. Confirm `.env` exists on the host or required variables are provided by the environment.
3. Confirm `.env` is not committed.
4. Confirm `XMPP_REGISTRATION_ENABLED=false`.
5. Confirm `JITSI_ENABLE_AUTH=1`.
6. Confirm `JITSI_ENABLE_GUESTS=0`.
7. Confirm public hostnames are placeholders in documentation and real values only in operator-owned configuration.
8. Confirm a recent backup exists before production changes.

Recommended startup order:

```bash
docker compose --env-file .env config
docker compose --env-file .env up -d postgres
python3 -m portal.app.cli migrate
docker compose --env-file .env up -d reverse-proxy prosody converse
docker compose --env-file .env up -d jitsi-prosody jitsi-jicofo jitsi-jvb jitsi-web
docker compose --env-file .env ps
```

Post-start checks:

1. Confirm PostgreSQL is running.
2. Confirm portal migrations completed.
3. Confirm reverse proxy is running.
4. Confirm chat frontend loads through the chat hostname.
5. Confirm Prosody WebSocket or BOSH paths route through the reverse proxy.
6. Confirm Jitsi web loads through the meeting hostname.
7. Confirm Jitsi media port is reachable only where the deployment requires it.
8. Confirm admin UI remains role-gated.
9. Confirm audit events can still be reviewed.

Do not invite real users until startup checks pass.

## 3. Service Shutdown Procedure

Shutdown should avoid data loss and preserve review records.

Planned shutdown steps:

1. Notify approved administrators through the local approved contact path if users may be affected.
2. Pause new invites, verification decisions, room access changes, and meeting creation where practical.
3. Confirm no backup or restore is running.
4. Record the reason and time in operator notes.
5. Stop public-facing services first if the shutdown is for maintenance.
6. Stop dependent services.
7. Stop PostgreSQL last.

Example command:

```bash
docker compose --env-file .env down
```

Shutdown rules:

- Do not delete volumes during routine shutdown.
- Do not delete backups during routine shutdown.
- Do not delete audit events.
- Do not rotate secrets unless the shutdown is part of an exposure response.
- Preserve logs when shutdown follows an incident.

## 4. Restart Procedures

Restart only the service or service group needed. Run health checks after each restart.

### Portal

Use when portal admin UI, CLI workflow, migrations, invite, verification, room, or meeting token commands fail.

Procedure:

1. Confirm PostgreSQL is healthy.
2. Preserve relevant portal logs and audit context if this follows an incident.
3. Restart the portal service or rerun the portal command that failed.
4. Check admin UI access.
5. Check recent audit events.

Example:

```bash
docker compose --env-file .env restart portal
python3 -m portal.app.cli migrate
```

Portal restart must not bypass admin role checks or create users directly.

### Prosody

Use when browser chat login, XMPP WebSocket, BOSH, or room access fails.

Procedure:

1. Confirm `XMPP_REGISTRATION_ENABLED=false`.
2. Confirm federation remains disabled.
3. Preserve Prosody logs if access widened or account state looks wrong.
4. Restart Prosody.
5. Check chat transport routes through Caddy.
6. Test with disposable approved and denied accounts where available.

Example:

```bash
docker compose --env-file .env restart prosody
```

Do not publish Prosody internal ports to fix a browser transport issue.

### Jitsi

Use when meeting pages fail, JWT validation fails, media fails, or Jitsi components disconnect.

Procedure:

1. Confirm `JITSI_ENABLE_AUTH=1`.
2. Confirm `JITSI_ENABLE_GUESTS=0`.
3. Confirm `JWT_ALLOW_EMPTY=0` where present in generated Jitsi configuration.
4. Preserve Jitsi logs if token misuse, guest misuse, or public room creation is suspected.
5. Restart Jitsi components in a controlled group.
6. Confirm the meeting hostname routes through Caddy.
7. Issue a test token through the portal for an allowed user.
8. Confirm unauthorized users cannot create rooms.

Example:

```bash
docker compose --env-file .env restart jitsi-prosody jitsi-jicofo jitsi-jvb jitsi-web
```

Do not disable JWT authentication to restore meeting access.

### Reverse Proxy

Use when public HTTP or HTTPS routes fail, TLS renewal fails, WebSocket routing fails, or an upstream route is wrong.

Procedure:

1. Validate Compose configuration.
2. Confirm public hostname variables are set in operator-owned configuration.
3. Preserve Caddy logs if routing exposed the wrong service.
4. Restart the reverse proxy.
5. Check portal, chat, XMPP browser transport, and meeting routes.
6. Confirm internal services are still not exposed directly.

Example:

```bash
docker compose --env-file .env config
docker compose --env-file .env restart reverse-proxy
```

Do not add manual TLS certificates to the repository.

## 5. Health Check Procedures

Health checks should start with service state, then routes, then workflow checks.

Service checks:

```bash
docker compose --env-file .env ps
```

Configuration checks:

```bash
docker compose --env-file .env config
```

Portal checks:

```bash
python3 -m portal.app.cli migrate
```

Route checks:

- Portal hostname loads through the reverse proxy.
- Chat hostname loads the Converse.js frontend.
- Chat hostname routes `/xmpp-websocket` and `/http-bind` to Prosody.
- Meeting hostname loads Jitsi web.
- Jitsi media port works where required by deployment.

Workflow checks with fake or approved test data:

- Admin can view users, groups, roles, invites, verification requests, rooms, and audit events.
- Admin can create a disposable invite.
- Expired, revoked, and used single-use invites are rejected.
- Verification approval and rejection require an admin.
- Room access follows role and group policy.
- Jitsi token issuance is role-gated.
- Backup script completes.

Health checks must not use real secrets, production invite tokens, or private room content in public notes.

## 6. Log Inspection Procedures

Inspect the smallest useful log window.

General command shape:

```bash
docker compose --env-file .env logs --tail=200 SERVICE_NAME
```

Recommended service targets:

| Service          | Check For |
| ---------------- | --------- |
| `reverse-proxy`  | TLS errors, upstream failures, WebSocket routing errors. |
| `portal`         | Migration failures, admin UI errors, authorization failures. |
| `postgres`       | Startup errors, connection errors, disk or data warnings. |
| `prosody`        | Auth failures, WebSocket or BOSH errors, MUC errors. |
| `converse`       | Static frontend serving errors. |
| `jitsi-web`      | Web route and JWT validation errors. |
| `jitsi-prosody`  | Internal Jitsi auth and component errors. |
| `jitsi-jicofo`   | Conference focus and component connection errors. |
| `jitsi-jvb`      | Media bridge and connectivity errors. |

Never copy into notes or public support channels:

- Passwords.
- Session cookies.
- JWT secrets or token bodies.
- Invite tokens.
- Recovery tokens.
- Message bodies.
- Private room contents.
- Full request bodies.
- `.env` contents.
- TLS private keys.
- Backup private paths where sensitive.

Prefer portal audit events for trust decisions and service logs for operational faults.

## 7. Backup Execution Procedure

Backups are local filesystem backups for the current stage.

Pre-backup checks:

1. Confirm `.env` exists or required variables are set.
2. Confirm `BACKUP_ROOT` points outside public web routes.
3. Confirm backup output is excluded from Git.
4. Confirm there is enough disk space.
5. Confirm the backup will not interrupt a restore or migration.

Execution:

```bash
scripts/backup.sh
scripts/list-backups.sh
```

Post-backup checks:

1. Confirm a timestamped backup set exists.
2. Confirm the manifest exists.
3. Confirm PostgreSQL dump exists and is non-empty.
4. Confirm Prosody data and configuration are included.
5. Confirm Jitsi configuration and data are included where present.
6. Confirm reverse proxy data is included where managed by the stack.
7. Confirm `.env.example` and docs snapshot or source commit reference are included where the script supports it.
8. Confirm no secret values appear in the manifest.

Backups must be treated as sensitive community records.

## 8. Restore Execution Procedure

Restore is high risk. Use a disposable or approved restore target whenever possible.

Pre-restore checks:

1. Confirm the restore target environment.
2. Confirm the backup environment matches the target.
3. Confirm the selected backup timestamp.
4. Confirm the current target data has been preserved or is disposable.
5. Confirm `.env` is available from operator-owned secret storage.
6. Confirm required secrets are not placeholders in production.
7. Confirm enough disk space exists.
8. Confirm public registration will remain disabled.
9. Confirm federation will remain disabled.
10. Confirm Jitsi authentication will remain enabled.

Execution shape:

```bash
scripts/list-backups.sh
RESTORE_CONFIRM=restore scripts/restore.sh PATH_TO_BACKUP
```

Restore order:

1. Restore repository checkout from Git.
2. Restore `.env` from operator secret storage.
3. Restore Docker volumes or backup directories.
4. Restore PostgreSQL.
5. Start PostgreSQL.
6. Run portal migrations or schema checks.
7. Start portal and confirm admin access.
8. Review users, roles, invites, verification records, rooms, meetings, suspensions, and audit events.
9. Start reverse proxy.
10. Start Prosody and Converse.js.
11. Start Jitsi components.
12. Run route and workflow health checks.

If restore exposes or may expose secrets, rotate the affected secrets before reopening public access.

## 9. Incident Response Steps

Incident response should contain risk first, then preserve records, repair access, and notify through approved paths.

Steps:

1. Identify the affected service, account, invite, room, meeting, route, backup, or secret.
2. Stop affected public routes or services if current exposure is unsafe.
3. Preserve relevant logs, audit events, backup manifests, and operator notes.
4. Revoke exposed invites, guest links, meeting tokens, or sessions where supported.
5. Suspend affected accounts if account compromise or abuse is suspected.
6. Rotate exposed or suspected secrets.
7. Restore from backup only if data integrity cannot be repaired safely.
8. Confirm public registration remains disabled.
9. Confirm open federation remains disabled.
10. Confirm Jitsi authentication remains enabled.
11. Confirm internal service ports remain private.
12. Notify approved administrators and affected users through the approved local path.
13. Record final action and follow-up review.

Do not delete audit records to hide mistakes. Corrections should create new records or operator notes.

## 10. User Issue Triage

User issue triage should separate account state, client trouble, room access, meeting access, and service outage.

Initial questions for the administrator:

- Is the user invited, pending, approved, denied, suspended, or disabled?
- Was the invite expired, revoked, already used, or reusable?
- Is the issue in portal, chat, a room, or a meeting?
- Is the issue affecting one user, one group, or everyone?
- Is there a recent audit event explaining the change?
- Is there a service outage in `docker compose ps`?

Common responses:

| Issue | First Check |
| ----- | ----------- |
| Cannot redeem invite | Invite status, expiry, reusable flag, and audit event. |
| Cannot see rooms | User status, group membership, roles, room policy, suspension. |
| Cannot sign in to chat | Prosody account state, browser transport, user suspension. |
| Cannot join meeting | Meeting status, user role, guest approval, token expiry. |
| Account says pending | Admin review status and verification request status. |
| Account suspended | Suspension reason and restoring admin authority. |

Do not expose private verification notes, raw tokens, internal hostnames, or service logs to ordinary users.

## 11. Verification Issue Handling

Verification issues affect trust labels and room or meeting access.

Procedure:

1. Confirm the request type is `clergy`, `monastic`, or `parish_admin`.
2. Confirm the requesting account is not suspended or disabled.
3. Confirm the deciding administrator has the correct scope.
4. Confirm the request has not already been decided.
5. Review local parish, diocesan, or monastic policy outside the platform where needed.
6. Approve or reject through the portal workflow.
7. Store a short rejection reason if rejected.
8. Confirm the matching role is assigned only for approved requests.
9. Confirm audit events exist for request creation and decision.

Rules:

- Users must not approve their own privileged status.
- Users must not self-assign clergy, monastic, parish admin, diocesan admin, or platform admin roles.
- Internal verification notes remain admin-only.
- Revocation or correction should create a new audit event.

## 12. Room and Channel Issue Handling

Room issues usually come from account state, group membership, role state, room scope, or Prosody sync limits.

Procedure:

1. Identify the room and its scope.
2. Confirm the user's account status.
3. Confirm the user's group memberships.
4. Confirm the user's roles.
5. Confirm explicit room membership for `invite_only` rooms.
6. Confirm the user is not suspended or disabled.
7. Confirm the room is not exposing names to unauthorized users.
8. Check Prosody logs only if portal policy says access should work.
9. Record access changes in audit events.

Supported room scopes:

- `public_to_members`
- `group_only`
- `clergy_only`
- `monastic_only`
- `admin_only`
- `invite_only`

Do not make a room more public to fix one user's access. Fix the user's membership, role, or explicit room access where policy allows it.

## 13. Meeting Issue Handling

Meeting issues should be checked through portal policy before Jitsi logs.

Procedure:

1. Confirm the meeting record exists and is active.
2. Confirm the requester is approved and not suspended.
3. Confirm the requester has access to the linked room or group where applicable.
4. Confirm the creator role is allowed by `JITSI_MEETING_CREATOR_ROLES`.
5. Confirm guests are explicitly approved and not expired.
6. Confirm the token has not expired.
7. Confirm `JITSI_ENABLE_AUTH=1`.
8. Confirm `JITSI_ENABLE_GUESTS=0`.
9. Check `jitsi-web`, `jitsi-prosody`, `jitsi-jicofo`, and `jitsi-jvb` logs for operational failures.
10. Issue a fresh test token only after access checks pass.

Do not disable JWT authentication or enable anonymous guests to fix a meeting issue.

## 14. Emergency Lockdown Procedure

Emergency lockdown is for suspected compromise, unsafe public exposure, active abuse, or identity data uncertainty.

Lockdown steps:

1. Stop or isolate affected public routes.
2. If scope is unclear, stop portal, chat, and meeting public access through the reverse proxy.
3. Keep PostgreSQL and data volumes preserved.
4. Preserve logs, audit events, backup manifests, and operator notes.
5. Revoke active unsafe invites.
6. Suspend compromised or abusive accounts.
7. Stop new meeting token issuance.
8. Rotate exposed secrets.
9. Confirm public registration remains disabled.
10. Confirm open federation remains disabled.
11. Confirm Jitsi authentication remains enabled.
12. Create a backup of the preserved state if safe.
13. Restore service only after administrator review.

Example containment command:

```bash
docker compose --env-file .env stop reverse-proxy
```

Use narrower service stops when the affected service is known. Do not delete volumes during lockdown.

## 15. Rollback Plan

Operational rollback should return the stack to the last known-good state without deleting trust records.

Rollback steps:

1. Identify the change, command, service, route, invite, verification decision, room change, meeting change, or restore that caused the problem.
2. Stop affected public routes or services if current behavior is unsafe.
3. Preserve current data, logs, audit events, backup manifests, and operator notes.
4. Restore the last known-good configuration or service state.
5. Restore data from a same-environment backup only if data integrity cannot be repaired safely.
6. Rotate secrets if exposure is suspected.
7. Confirm public registration remains disabled.
8. Confirm open federation remains disabled.
9. Confirm Jitsi authentication remains enabled.
10. Confirm admin routes remain role-gated.
11. Confirm internal service ports remain private.
12. Confirm users, roles, verification records, rooms, meetings, and audit events are intact.
13. Run health checks.
14. Record the rollback result.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, reverse proxy data, backups, or unrelated service configuration unless a separate reviewed retention or data repair process explicitly requires it.
