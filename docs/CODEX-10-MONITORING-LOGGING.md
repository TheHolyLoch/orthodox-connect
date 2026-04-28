# Orthodox Connect Monitoring and Logging

## Logging Goals

Logging and observability should help trusted operators keep Orthodox Connect reliable, secure, and recoverable without turning logs into a parallel store of private community activity.

Goals:

- Detect service outages and failed upgrades quickly.
- Support incident response for account abuse, invite misuse, and administrator actions.
- Confirm backups, restores, and migrations are working.
- Keep enough operational context to troubleshoot failures.
- Avoid logging message content, secrets, private notes, or unnecessary personal data.

## What Must Be Logged

Required operational logs:

- Service start, stop, restart, and crash events.
- Database migration start, success, and failure.
- Backup start, success, failure, and restore actions.
- Authentication success and failure metadata where login exists.
- Admin actions.
- Invite creation, redemption, expiration, and revocation.
- Verification request creation, approval, and rejection.
- Role, group, room, and meeting access changes.
- Meeting creation and token issuance metadata.
- Reverse proxy routing errors and upstream failures.
- Prosody authentication and connection failures.
- Jitsi service errors and meeting join failures.

## What Must Not Be Logged

Never log:

- Passwords.
- Session cookies.
- JWT signing secrets or issued token bodies.
- Invite tokens.
- Recovery tokens.
- Message bodies.
- Private room contents.
- Full request bodies.
- Full database connection URLs with passwords.
- `.env` contents.
- TLS private keys, onion private keys, or backup encryption keys.
- Sensitive verification notes beyond controlled audit fields.

Logs should prefer stable IDs, event types, and coarse metadata over full personal details.

## Log Retention Policy

Default retention should be short unless a deployment has a documented reason to keep logs longer.

Recommended retention:

| Log Type              | Default Retention | Notes |
| --------------------- | ----------------- | ----- |
| Container stdout logs | 7 to 14 days      | Enough for basic troubleshooting. |
| Reverse proxy access  | 7 to 14 days      | Avoid long-term browsing metadata. |
| Security event logs   | 30 to 90 days     | Keep only reviewed metadata. |
| Audit events          | Policy-defined    | Stored in PostgreSQL and treated as records. |
| Backup logs           | Match backup retention | Needed to prove backup health. |
| Debug logs            | Disabled by default | Enable briefly for troubleshooting only. |

Retention must be reviewed before enabling federation, Tor access, or library service logging.

## Log Storage Locations

MVP storage:

- Container logs stay in the Docker logging driver on the host.
- Portal audit events stay in PostgreSQL.
- Backup and restore output stays in operator terminal output or local operator logs if redirected.
- No external logging provider is configured.

Future storage options:

- Local log directory excluded from Git.
- Local syslog or journald integration.
- Self-hosted log aggregation after privacy review.
- Encrypted off-host log archive only when required by policy.

Logs must not be committed to Git.

## Service-Level Logging Requirements

### Portal

Portal logs should include:

- Migration results.
- CLI command failures.
- Admin UI errors.
- Authentication and authorization failures when login is implemented.
- Invite, verification, room, meeting, and role actions through audit events.

Portal logs must not include invite tokens except at creation time where the CLI or admin UI intentionally returns the token to the operator. Persistent logs should store invite IDs, not raw tokens.

### Prosody

Prosody logs should include:

- Service start and configuration errors.
- Authentication failures.
- Connection failures.
- MUC room creation or access-control errors where available.
- Federation attempts if federation is later enabled.

Prosody logs must not include message bodies or private room content. Public registration and open federation should remain disabled unless a later reviewed design changes that policy.

### Jitsi

Jitsi logs should include:

- Service start and component connection errors.
- JWT validation failures.
- Meeting join failures.
- Jicofo and JVB connectivity problems.
- Media bridge health and restart events.

Jitsi logs must not include JWT secrets, full JWT token bodies, meeting passwords, or private participant notes.

### Reverse Proxy

Reverse proxy logs should include:

- Upstream service failures.
- TLS and certificate renewal problems.
- WebSocket routing errors.
- HTTP status codes and request paths where needed for troubleshooting.

Reverse proxy logs should avoid query strings by default because invite tokens, recovery tokens, or other sensitive values may appear there.

## Audit Log Requirements

Audit logs are different from service logs. They are records of trust and access decisions.

Audit events should include:

- Actor ID.
- Target resource ID.
- Event type.
- Timestamp.
- Scope.
- Reason or note where needed.
- Minimal route or source metadata if policy allows it.

Audit events should cover:

- Invites.
- Verification decisions.
- Role changes.
- Group membership changes.
- Room creation and membership changes.
- Meeting creation and token issuance.
- Federation approval, scope changes, and revocation when implemented.
- Library import and access changes when implemented.

Audit records should be append-only from the application perspective.

## Health Check Strategy

MVP health checks should be simple and local.

Checks:

- `docker compose ps` shows expected services running.
- Reverse proxy responds on public HTTP and HTTPS routes.
- Chat frontend loads through the reverse proxy.
- Prosody browser transport paths respond through the chat route.
- PostgreSQL accepts portal connections.
- Portal migrations can run without pending errors.
- Jitsi web route loads and internal Jitsi components stay connected.
- Backup script completes against disposable or production data as policy allows.

Future health checks:

- Portal `/health` endpoint after production packaging.
- Prosody module or admin-safe health endpoint.
- Jitsi component health endpoint review.
- Synthetic login and chat transport checks using test accounts.
- Backup age and restore test status.

Health checks must not require public registration, real users, or real secrets in Git.

## Alerting Model

MVP alerting can be operator-driven.

Minimal alert sources:

- Container not running.
- Reverse proxy route down.
- TLS renewal failure.
- PostgreSQL connection failure.
- Backup failure.
- Disk usage near capacity.
- Repeated authentication failures.
- Jitsi media bridge unavailable.

Future alerting:

- Local-only alert scripts.
- Email or chat alerts after notification policy is reviewed.
- Self-hosted monitoring dashboard.
- Per-service uptime and error-rate alerts.

External alerting providers should not be added until data exposure and account ownership are reviewed.

## Minimal MVP and Future Expansion

Minimal MVP approach:

- Use Docker logs.
- Keep audit events in PostgreSQL.
- Use manual health checks and backup verification commands.
- Keep retention short.
- Avoid central log aggregation.

Future expansion:

- Package the portal with structured application logging.
- Add service health endpoints.
- Add local monitoring dashboards.
- Add alert rules for uptime, backups, disk, and authentication abuse.
- Add privacy-reviewed log aggregation.
- Add federation, Tor, and library-specific metrics only after those features exist.

## Privacy Considerations

Logs can reveal sensitive community metadata even without message bodies.

Sensitive metadata includes:

- Usernames and account IDs.
- IP addresses.
- User agents.
- Room names.
- Meeting names.
- Login times.
- Invite timing.
- Verification and role-change timing.
- Federation partner domains when implemented.
- Library search and reading activity when implemented.

Privacy rules:

- Collect the least data needed to operate safely.
- Keep debug logging off by default.
- Avoid long retention.
- Limit log access to trusted operators.
- Treat logs and backups as sensitive records.
- Review logging before enabling Tor, federation, or library access.

## Failure Scenarios and Detection

| Failure Scenario          | Detection Method                              | Operator Action |
| ------------------------- | --------------------------------------------- | --------------- |
| Reverse proxy down        | Public routes fail, container stopped.         | Restart service, inspect route and certificate logs. |
| PostgreSQL unavailable    | Portal commands fail, migrations fail.         | Check container state, disk, volume, and backup status. |
| Prosody unavailable       | Chat login or transport fails.                 | Check Prosody logs and reverse proxy upstream errors. |
| Jitsi unavailable         | Meeting join fails or media bridge disconnects.| Check Jitsi web, Jicofo, Prosody, and JVB logs. |
| Disk nearly full          | Host or Docker volume usage alert.             | Free space, prune safe logs, review backups. |
| Backup failed             | Backup script exits non-zero or missing output.| Rerun after checking PostgreSQL and volume access. |
| TLS renewal failed        | Reverse proxy certificate errors.              | Check DNS, public ports, ACME email, and Caddy logs. |
| Abuse spike               | Repeated auth failures or invite failures.     | Revoke invites, suspend accounts, review audit events. |
| Suspicious admin action   | Unexpected audit event.                        | Review actor, revoke access if needed, preserve logs. |

## Backup of Logs

Logs should not be backed up by default.

Exceptions:

- Audit events in PostgreSQL are included in database backups.
- Backup and restore evidence may be retained with backup metadata.
- Security incident logs may be copied to operator-controlled storage for review.

Rules:

- Do not back up routine container logs unless a deployment policy requires it.
- Do not include logs in Git.
- Do not include logs in public support requests without review.
- If logs are archived, encrypt and protect them like backups.

## Rollback Plan

Monitoring and logging changes must be easy to disable.

Rollback steps:

1. Disable new log collection or alerting rules.
2. Confirm Docker logs and portal audit events still work.
3. Remove access to any faulty dashboard or log archive.
4. Preserve incident evidence if rollback is due to a security event.
5. Delete accidental logs containing secrets if policy allows deletion.
6. Rotate any secret that appeared in logs.
7. Restore the previous retention settings.
8. Document what was disabled and why.

Rollback must not delete portal audit records, PostgreSQL data, service volumes, backups, or unrelated application state.
