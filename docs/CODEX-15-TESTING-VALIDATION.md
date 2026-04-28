# Orthodox Connect Testing and Validation

## Testing Goals

Testing should prove that the MVP keeps the trust model intact while the stack starts, routes, stores state, and recovers from failure.

Goals:

- Confirm invite-only onboarding works.
- Confirm users cannot self-assign privileged roles.
- Confirm clergy, monastic, and parish admin verification stays administrator-controlled.
- Confirm room access follows roles, group membership, explicit membership, and suspension state.
- Confirm Jitsi meeting creation and token issuance remain role-gated.
- Confirm public registration and open federation remain disabled.
- Confirm backups can be created and restored with disposable data.
- Confirm service routes work through the reverse proxy.
- Confirm secrets, tokens, backups, logs, and generated state are not committed.

Testing should favor repeatable checks first, then manual review for workflows that depend on administrator judgment.

## MVP Test Coverage Scope

Current MVP validation should cover implemented repository behavior only.

In scope:

- Docker Compose configuration.
- Reverse proxy routing.
- Prosody configuration defaults.
- Converse.js frontend configuration.
- Portal migrations.
- Portal CLI workflows for invites, verification, rooms, meetings, and audit records.
- Minimal admin UI access and views.
- Jitsi JWT access model.
- Local backup, restore, and backup listing scripts.
- Security defaults documented in `.env.example` and service configs.

Out of scope for current tests:

- Public registration.
- Open federation.
- Tor onion access.
- IRC fallback or bridge.
- Library service integration.
- Branded mobile app.
- Automated moderation.
- Email delivery.
- Prosody account provisioning from portal data.

Out-of-scope items may have design checks, but should not be treated as implemented features.

## Unit Testing Strategy

No dedicated Python test framework is currently present in the repository. Do not add one until a later implementation pass approves it.

When a test framework is added later, unit tests should focus on portal logic that can be tested without Docker:

- Invite token status checks.
- Invite expiry and revocation rules.
- Single-use versus reusable invite behavior.
- Verification request state transitions.
- Role assignment from approved verification decisions.
- Room access calculation.
- Room membership creation rules.
- Meeting creator role checks.
- Guest token eligibility.
- Audit event creation helpers.
- Config parsing for required environment variables.

Unit tests should avoid real secrets, real parish names, real users, and production data. Test fixtures should use disposable IDs and obvious fake values.

## Integration Testing Strategy

Integration tests should validate interactions across services and persistent state.

Current integration checks can use Compose and portal CLI commands:

- `docker compose --env-file .env config`
- `docker compose --env-file .env up -d postgres`
- `python3 -m portal.app.cli migrate`
- `docker compose --env-file .env up -d reverse-proxy prosody converse`
- `docker compose --env-file .env up -d jitsi-web jitsi-prosody jitsi-jicofo jitsi-jvb`
- `scripts/backup.sh`
- `scripts/list-backups.sh`
- `scripts/restore.sh` against disposable data only.

Integration tests must use a test `.env`, disposable database state, disposable Docker volumes, and no real users or secrets.

## Manual Testing Checklist

Manual MVP validation should confirm:

- `.env` exists locally and is not tracked by Git.
- `.env.example` contains placeholders only.
- Compose config renders without errors.
- Only required public ports are exposed.
- Caddy routes portal, chat, XMPP browser transports, and Jitsi web.
- Prosody registration is disabled.
- Prosody federation is disabled.
- Converse.js points at configured BOSH or WebSocket URLs.
- Portal migrations apply cleanly.
- Admin UI starts from the repo and shows expected views.
- Internal verification notes are not shown to ordinary users.
- Jitsi requires JWT authentication.
- Backup scripts create local backup output.
- Restore is tested only against disposable data.
- Logs do not print passwords, invite tokens, recovery tokens, JWT secrets, or `.env` contents.

Manual checks should record the date, operator, environment, commands used, and result.

## Invite Workflow Tests

Invite tests should cover:

- Admin can create an invite.
- Invite records creator ID.
- Invite has an expiry time.
- Invite can be listed.
- Invite can be revoked.
- Valid invite can be redeemed.
- Redeemed invite creates a limited pending user.
- Expired invite is rejected.
- Revoked invite is rejected.
- Already-used single-use invite is rejected.
- Reusable invite behavior is explicit when enabled.
- Redeemed user cannot self-assign verified or privileged roles.
- Invite creation, revocation, and redemption create audit events.

Validation should use fake user data and test-only tokens.

## Verification Workflow Tests

Verification tests should cover:

- User can submit a verification request.
- Supported request types are `clergy`, `monastic`, and `parish_admin`.
- Admin can list pending verification requests.
- Admin can approve a request.
- Admin can reject a request with a reason.
- Approved clergy request assigns `clergy_verified`.
- Approved monastic request assigns `monastic_verified`.
- Approved parish admin request assigns `parish_admin`.
- Rejected request does not assign a privileged role.
- Non-admin users cannot approve or reject requests.
- Users cannot approve their own privileged status.
- Verification request creation, approval, and rejection create audit events.
- Suspended users do not appear as active verified users.

Tests should not automate spiritual, pastoral, disciplinary, or clergy judgment. They should only validate workflow controls.

## Role-Based Access Tests

Room access tests should cover each implemented scope:

- `public_to_members`
- `group_only`
- `clergy_only`
- `monastic_only`
- `admin_only`
- `invite_only`

Access checks should confirm:

- Approved members can access `public_to_members` rooms.
- Pending users cannot access member-only rooms.
- Suspended users cannot access rooms.
- Group membership is required for `group_only` rooms.
- `clergy_verified` is required for `clergy_only` rooms.
- `monastic_verified` is required for `monastic_only` rooms.
- Admin role is required for `admin_only` rooms.
- Explicit membership is required for `invite_only` rooms.
- Room membership records are created only when access rules allow it.
- Room creation creates an audit event.
- Room access changes create audit events.
- Room membership changes create audit events.

Prosody MUC behavior should be checked only where current configuration supports it. Portal policy remains the source of truth until full Prosody account provisioning and synchronization are implemented.

## Jitsi Access Tests

Jitsi tests should cover:

- Jitsi services render in Compose config.
- Jitsi web route is served through the reverse proxy.
- `JITSI_ENABLE_AUTH=1`.
- `JITSI_ENABLE_GUESTS=0` for MVP.
- JWT app ID and secret are required through environment variables.
- Meeting creation is limited to allowed roles.
- Unauthorized users cannot create official meeting rooms.
- Meeting token issuance creates an audit event.
- User meeting tokens are issued only for allowed users.
- Guest access works only for explicitly allowed guests.
- Guest token issuance creates an audit event.
- Meeting names alone do not grant access.
- Expired tokens are rejected by policy.
- Rotated JWT secrets invalidate old tokens.

Tests should not use real meeting names, real guests, or production JWT secrets.

## Backup and Restore Tests

Backup validation should cover:

- `scripts/backup.sh` loads `.env`.
- Backup output goes under `BACKUP_ROOT`.
- Backup output is timestamped.
- PostgreSQL logical dump is created.
- Prosody data and config are included.
- Jitsi config and data are included when present.
- Reverse proxy data is included where managed by the stack.
- Backup manifest does not print secret values.
- Backup output is excluded from Git.
- `scripts/list-backups.sh` lists available backups.

Restore validation should cover:

- `scripts/restore.sh` loads `.env`.
- Restore refuses to run without the expected confirmation value.
- Restore refuses missing backup paths.
- Restore is tested against disposable data before production use.
- Restored portal data includes users, roles, invites, rooms, meetings, and audit events.
- Restored Prosody data starts cleanly.
- Restored Jitsi config starts cleanly.
- Public registration remains disabled after restore.
- Federation remains disabled after restore.

Restore tests must never overwrite production data during routine validation.

## Failure Simulation Tests

Failure simulation should use disposable data and test environments.

Recommended simulations:

- Stop `reverse-proxy` and confirm public routes fail clearly.
- Stop `postgres` and confirm portal commands fail safely.
- Stop `prosody` and confirm chat transport fails clearly.
- Stop Jitsi components and confirm meeting access fails clearly.
- Run portal migrations twice and confirm they are safe to repeat or fail clearly.
- Use an expired invite and confirm redemption is rejected.
- Use a revoked invite and confirm redemption is rejected.
- Try room access with a suspended user and confirm denial.
- Temporarily remove required environment variables in a test `.env` and confirm services fail closed.
- Run backup with an invalid `BACKUP_ROOT` and confirm clear failure.
- Run restore without restore confirmation and confirm refusal.

Failure tests should not require public registration, real users, real secrets, or production domains.

## Security Validation Checks

Security validation should confirm:

- `.env` is not tracked.
- Backups are not tracked.
- Logs are not tracked.
- Real secrets are not present in committed files.
- `.env.example` uses placeholders only.
- Public registration remains disabled.
- Open federation remains disabled.
- Internal service ports are not published unless required.
- Jitsi room creation remains authenticated.
- Anonymous public Jitsi room creation remains disabled.
- Portal admin routes require admin roles.
- Admin actions create audit events.
- Verification decisions create audit events.
- Suspended accounts lose access.
- Reverse proxy security headers remain configured.
- Debug logging is not enabled by default for production.
- Backup manifests avoid secret leakage.

Suggested repository checks:

```bash
git status --short
docker compose --env-file .env config
rg 'TODO|TBD|CHANGE_ME|secret|password' README.md docs .env.example
rg 'BEGIN .*PRIVATE KEY|JITSI_JWT_APP_SECRET=|POSTGRES_PASSWORD=' .
```

Operators should inspect matches manually because placeholder documentation may include variable names.

## Pre-Deployment Checklist

Before deployment:

- DNS records point to the host.
- Required public ports are open.
- `.env` exists only on the host or operator secret storage.
- Secrets are generated outside Git.
- `XMPP_REGISTRATION_ENABLED=false`.
- `JITSI_ENABLE_AUTH=1`.
- `JITSI_ENABLE_GUESTS=0`.
- Compose config renders cleanly.
- Portal migrations run cleanly.
- Admin UI starts.
- A disposable invite workflow test passes.
- A disposable verification workflow test passes.
- A disposable room access test passes.
- A disposable Jitsi token test passes.
- Backup script completes.
- Restore has been tested against disposable data.
- Operator emergency contacts are stored outside the repo.
- Known MVP limits are accepted by the operator.

Do not deploy with real parish data until restore and rollback paths have been tested.

## Post-Deployment Validation

After deployment:

- Public HTTPS routes load for portal, chat, and meetings.
- Caddy has obtained or loaded valid certificates.
- Chat frontend loads through the configured chat hostname.
- Prosody browser transport paths respond through the reverse proxy.
- Portal admin view shows users, groups, roles, invites, verification requests, rooms, and audit events.
- Admin can create a test invite.
- Test invite can be redeemed.
- Test pending user cannot self-assign privileged roles.
- Admin can approve or reject a test verification request.
- Room access checks return expected results for test users.
- Jitsi test meeting token works for an allowed test user.
- Unauthorized test user cannot create a meeting.
- Backup script completes after deployment.
- Logs do not show secrets, tokens, or private message bodies.

Remove or disable disposable test accounts and rooms after validation if the deployment policy requires it.

## Rollback Validation Steps

Rollback validation should confirm that a bad deployment can return to a known-good state.

Steps:

1. Record current commit, `.env` version, backup timestamp, and running service list.
2. Create a backup before the change.
3. Apply the change in a test environment first where possible.
4. Run the relevant validation checks.
5. If validation fails, stop affected public routes or services.
6. Restore the previous configuration or backup.
7. Confirm portal admin access.
8. Confirm users, roles, verification records, room access, meetings, and audit events are intact.
9. Confirm public registration remains disabled.
10. Confirm federation remains disabled.
11. Confirm Jitsi authentication remains enabled.
12. Confirm backups still run.
13. Record the rollback result.

Rollback must not delete audit events, verification records, users, rooms, backups, or unrelated service data.
