# Orthodox Connect Go-Live Checklist

## 1. Go-Live Goals

The go-live checklist confirms that an Orthodox Connect deployment is ready for a controlled first launch with real users.

Goals:

- Confirm the environment is configured with operator-owned values.
- Confirm secrets are generated outside Git.
- Confirm public routes work through Caddy.
- Confirm TLS is active for real hostnames.
- Confirm invite-only onboarding works.
- Confirm manual verification and room access checks work.
- Confirm Jitsi access is authenticated and role-gated.
- Confirm backups and restore have been tested.
- Confirm operators can monitor the first launch.
- Confirm rollback is ready before invitations are sent.

Go-live is for the current MVP only. It does not include public registration, open federation, Tor onion access, IRC bridges, library integration, native mobile apps, automated Prosody provisioning, or advanced moderation tooling.

## 2. Pre-Launch Checklist

### Environment Configured

- [ ] Repository checkout is on the reviewed commit.
- [ ] No unreviewed local changes are present.
- [ ] `.env` exists on the host and is not tracked by Git.
- [ ] `.env.example` has been reviewed against the real `.env`.
- [ ] Local, staging, and production values are not mixed.
- [ ] Required Docker volumes are present or ready to be created.
- [ ] `docker compose --env-file .env config` renders without errors.

### Secrets Set

- [ ] PostgreSQL password is set in `.env`.
- [ ] Portal secret value is set in `.env`.
- [ ] Jitsi JWT app ID is set in `.env`.
- [ ] Jitsi JWT secret is set in `.env`.
- [ ] Prosody admin JID is set in `.env`.
- [ ] Backup path variables are set in `.env`.
- [ ] Secrets are not copied into README files, docs, logs, shell history snippets, tickets, or chat messages.
- [ ] Placeholder values have been replaced where the service requires real secrets.

### Domains Configured

- [ ] `ROOT_DOMAIN` is set.
- [ ] `PORTAL_DOMAIN` is set.
- [ ] `CHAT_DOMAIN` is set.
- [ ] `MEET_DOMAIN` is set.
- [ ] `LIBRARY_DOMAIN` is set only as a placeholder route.
- [ ] Public DNS points to the intended host.
- [ ] No public DNS records exist for PostgreSQL, Prosody admin interfaces, Jitsi internals, Docker, or host administration.
- [ ] Local development domains are not used for production users.

### TLS Active

- [ ] Caddy is the public HTTP and HTTPS entrypoint.
- [ ] Ports `80/tcp` and `443/tcp` are reachable where Caddy uses normal ACME issuance.
- [ ] Public portal route has a valid certificate.
- [ ] Public chat route has a valid certificate.
- [ ] Public meeting route has a valid certificate.
- [ ] No TLS private keys or certificate stores are committed to Git.
- [ ] Certificate renewal errors are absent from reverse proxy logs.

### Backups Tested

- [ ] `scripts/backup.sh` loads `.env`.
- [ ] Backup output is written under `BACKUP_ROOT`.
- [ ] Backup output is timestamped.
- [ ] PostgreSQL portal data is included.
- [ ] Prosody data and config are included.
- [ ] Jitsi config and data are included where present.
- [ ] Reverse proxy data is included where managed by the stack.
- [ ] Backup manifest avoids secret values.
- [ ] Backup output is excluded from Git.
- [ ] Latest backup location is known to at least two trusted operators where practical.

### Restore Tested

- [ ] `scripts/restore.sh` loads `.env`.
- [ ] Restore refuses to run without the required confirmation.
- [ ] Restore refuses missing backup paths.
- [ ] Restore has been tested against disposable or approved staging data.
- [ ] Restored portal data includes users, roles, invites, verification records, rooms, meetings, and audit events.
- [ ] Restored Prosody data starts cleanly.
- [ ] Restored Jitsi config starts cleanly.
- [ ] Public registration remains disabled after restore.
- [ ] Federation remains disabled after restore.

### Admin Accounts Verified

- [ ] At least one platform or local admin account is available for launch.
- [ ] A second trusted admin or operator is available where practical.
- [ ] Admin accounts are not shared accounts.
- [ ] Admin roles are assigned only to trusted people.
- [ ] Admin UI access is role-gated.
- [ ] Non-admin users cannot access admin-only views or actions.
- [ ] Emergency operator contact details are stored outside the repository.

### Invite Workflow Tested

- [ ] Admin can create an invite.
- [ ] Invite records creator, expiry, status, and reusable state.
- [ ] Invite can be listed.
- [ ] Invite can be revoked.
- [ ] Valid invite can be redeemed.
- [ ] Expired invite is rejected.
- [ ] Revoked invite is rejected.
- [ ] Already-used single-use invite is rejected.
- [ ] Redeemed invite creates a limited user state.
- [ ] Invite creation, revocation, and redemption create audit events.

### Verification Workflow Tested

- [ ] User can submit a `clergy` verification request.
- [ ] User can submit a `monastic` verification request.
- [ ] User can submit a `parish_admin` verification request.
- [ ] Admin can approve a verification request.
- [ ] Admin can reject a verification request with a reason.
- [ ] Approved request assigns the correct role.
- [ ] Rejected request does not assign a privileged role.
- [ ] User cannot approve their own privileged status.
- [ ] Verification request creation, approval, and rejection create audit events.

### Room Access Tested

- [ ] Portal can define rooms or channels.
- [ ] `public_to_members` access is tested.
- [ ] `group_only` access is tested.
- [ ] `clergy_only` access is tested.
- [ ] `monastic_only` access is tested.
- [ ] `admin_only` access is tested.
- [ ] `invite_only` access is tested.
- [ ] Room membership records are created only when access rules allow it.
- [ ] Suspended or unauthorized users are denied where the current workflow supports the check.
- [ ] Room creation, access changes, and membership changes create audit events.

### Jitsi Access Tested

- [ ] Jitsi web route loads through `MEET_DOMAIN`.
- [ ] `JITSI_ENABLE_AUTH=1`.
- [ ] `JITSI_ENABLE_GUESTS=0` for the MVP policy.
- [ ] JWT app ID and secret are set.
- [ ] Portal can create a meeting record for an allowed user.
- [ ] Portal can issue a meeting token for an allowed user.
- [ ] Unauthorized users cannot create official meetings.
- [ ] Guest access works only where explicitly allowed.
- [ ] Meeting creation and token issuance create audit events.
- [ ] Meeting names alone do not grant access.

## 3. Security Checklist

- [ ] `.env` is not tracked.
- [ ] Backup output is not tracked.
- [ ] Logs are not tracked.
- [ ] Real secrets are not present in committed files.
- [ ] Real domains are not added to docs or examples.
- [ ] Real user data is not committed.
- [ ] Public registration is disabled.
- [ ] `XMPP_REGISTRATION_ENABLED=false`.
- [ ] Prosody federation is disabled.
- [ ] Jitsi anonymous public room creation is disabled.
- [ ] Portal admin actions require admin roles.
- [ ] Users cannot self-assign privileged roles.
- [ ] Verification decisions require an admin user.
- [ ] PostgreSQL is not exposed publicly.
- [ ] Prosody native or admin ports are not exposed publicly.
- [ ] Jitsi internal services are not exposed publicly.
- [ ] Reverse proxy security headers are active where compatible with the service.
- [ ] Logs do not show passwords, invite tokens, recovery tokens, JWT secrets, JWT bodies, session cookies, or private message content.
- [ ] No production data appears in issue reports, screenshots, support requests, or public logs.

Suggested checks:

```bash
git status --short
docker compose --env-file .env config
rg 'BEGIN .*PRIVATE KEY|JITSI_JWT_APP_SECRET=|POSTGRES_PASSWORD=' .
```

Matches must be reviewed manually because placeholder variable names may appear in documentation.

## 4. Monitoring Readiness Checklist

- [ ] Operator knows how to run `docker compose ps`.
- [ ] Operator knows how to inspect reverse proxy logs.
- [ ] Operator knows how to inspect portal errors.
- [ ] Operator knows how to inspect Prosody logs.
- [ ] Operator knows how to inspect Jitsi logs.
- [ ] Operator knows how to confirm recent backup output.
- [ ] Operator knows where audit events are viewed.
- [ ] Disk space check procedure is known.
- [ ] TLS renewal failure check procedure is known.
- [ ] Repeated failed login, invite, or meeting access attempts have a review path where logs exist.
- [ ] No external monitoring provider is required for MVP go-live.

MVP monitoring may be manual. External monitoring services are future scope.

## 5. Documentation Readiness

- [ ] README setup instructions match the current repository.
- [ ] README production notes match Caddy, Docker Compose, and current services.
- [ ] README backup and restore commands match the scripts.
- [ ] `.env.example` includes required variables without real secrets.
- [ ] Architecture docs match current services.
- [ ] Identity and verification docs match current workflows.
- [ ] Security docs match current defaults.
- [ ] Operations and runbook docs are present.
- [ ] Acceptance criteria have been reviewed.
- [ ] Known MVP limitations are visible to operators.
- [ ] Future features are not documented as implemented.

## 6. User Onboarding Readiness

- [ ] First invited users are identified outside the repository.
- [ ] Initial invitation policy is agreed.
- [ ] Invite delivery path is agreed outside the platform.
- [ ] Reusable invites are disabled unless explicitly needed.
- [ ] Invite expiry policy is agreed.
- [ ] New users know who to contact if an invite fails.
- [ ] New users are told approval or verification may be required before full access.
- [ ] Admins know how to review pending users.
- [ ] Admins know how to revoke mistaken or leaked invites.
- [ ] No invite links are posted publicly.

## 7. Initial Group and Parish Setup

- [ ] Initial parish, monastery, mission, or group records are created with fake or approved production data.
- [ ] Initial admin roles are assigned.
- [ ] Initial ordinary roles are reviewed.
- [ ] Initial room list is reviewed for privacy.
- [ ] Sensitive room names do not expose pastoral, clergy, monastic, youth, or private details to unauthorized users.
- [ ] Default member room is tested.
- [ ] Clergy-only room is tested where needed.
- [ ] Monastic-only room is tested where needed.
- [ ] Admin-only room is tested.
- [ ] Initial meeting policy is agreed.
- [ ] Guest meeting access policy is agreed.
- [ ] Audit events for setup actions are reviewed.

## 8. Post-Launch Checklist

### Logs Monitored

- [ ] Reverse proxy logs checked after launch.
- [ ] Prosody logs checked after first chat tests.
- [ ] Jitsi logs checked after first meeting test.
- [ ] Portal errors checked after first invite and verification activity.
- [ ] Backup output checked after the first scheduled backup.
- [ ] Logs reviewed for accidental secret or token exposure.

### Performance Checked

- [ ] Portal admin UI responds with initial users and rooms.
- [ ] Chat frontend loads through the public chat hostname.
- [ ] Prosody browser transport remains reachable.
- [ ] First Jitsi meeting has acceptable audio and video for the small launch group.
- [ ] Host disk use is checked.
- [ ] Host memory and CPU are checked through the operator's normal host tools.
- [ ] Backup duration is acceptable for the initial dataset.

### User Feedback Loop

- [ ] Users know where to report login, invite, chat, or meeting problems.
- [ ] Admins have a process for collecting early issues.
- [ ] Admins can distinguish user support issues from security incidents.
- [ ] Early feedback is reviewed before inviting larger groups.
- [ ] Known issues are recorded without real secrets, private notes, or raw tokens.

## 9. Rollback Readiness

- [ ] Last known-good commit is recorded.
- [ ] Production `.env` location is known.
- [ ] Latest backup location is known.
- [ ] Restore procedure has been tested.
- [ ] Operator knows how to stop public routes or affected services.
- [ ] Operator knows how to restore PostgreSQL data.
- [ ] Operator knows how to restore Prosody data.
- [ ] Operator knows how to restore Jitsi config and data.
- [ ] Operator knows how to restore reverse proxy data where needed.
- [ ] Admin contact path is available outside the platform.
- [ ] User notification path is available outside the platform.

## 10. Rollback Triggers

Rollback should be considered if any of these occur:

- Public registration becomes available.
- Open federation becomes available unexpectedly.
- Internal service ports are exposed publicly.
- Jitsi allows anonymous public room creation.
- Admin routes are accessible to non-admin users.
- Users can self-assign privileged roles.
- Verification decisions are not tied to admin users.
- Invite redemption accepts expired, revoked, or already-used single-use invites.
- Backups fail and cannot be corrected before launch.
- Restore cannot be completed against disposable or approved data.
- TLS fails for public routes.
- DNS points users to the wrong host.
- Secrets, invite tokens, JWT bodies, logs, or private data are exposed.
- Portal identity, role, room, meeting, or audit data cannot be trusted.

If identity data cannot be trusted, keep chat and meetings offline until portal state is reviewed.

## 11. Rollback Procedure Summary

Rollback steps:

1. Stop sending new invites.
2. Disable affected public routes or services if exposure is possible.
3. Preserve current logs, audit events, backup manifests, and operator notes.
4. Identify the last known-good commit, `.env`, backup, and configuration.
5. Restore to a disposable target first where practical.
6. Restore production only after portal identity and access data pass review.
7. Rotate secrets if exposure is suspected.
8. Confirm public registration remains disabled.
9. Confirm open federation remains disabled.
10. Confirm Jitsi authentication remains enabled.
11. Confirm admin routes remain role-gated.
12. Confirm internal service ports remain private.
13. Confirm backups still run.
14. Notify administrators before ordinary users.
15. Record the rollback result.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, reverse proxy data, backups, or unrelated service configuration.

## 12. Sign-Off Requirements

Go-live requires sign-off from the responsible operators before real users are invited.

Minimum sign-off:

- [ ] Technical operator confirms deployment, DNS, TLS, backups, restore, and monitoring readiness.
- [ ] Platform or local admin confirms invite, verification, room, meeting, and admin UI readiness.
- [ ] Security reviewer or trusted maintainer confirms the security checklist.
- [ ] Documentation reviewer confirms README and docs match implemented behavior.
- [ ] Parish, diocesan, monastic, or community authority confirms the initial user and group scope where applicable.
- [ ] Rollback owner confirms rollback steps and contact paths.

Sign-off records should be stored in operator notes or another private administrative record. Do not commit real names, private contacts, signatures, domains, or secrets to this repository.
