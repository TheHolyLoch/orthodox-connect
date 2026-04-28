# Orthodox Connect MVP Acceptance Criteria

## 1. Acceptance Goals

MVP acceptance should prove that Orthodox Connect can run as a small self-hosted private communications stack without weakening the project trust model.

Goals:

- Confirm the implemented stack starts and routes through the reverse proxy.
- Confirm portal data, invites, verification, roles, rooms, meetings, and audit records work with disposable data.
- Confirm Prosody and Converse.js provide the current web chat foundation.
- Confirm Jitsi meeting access remains authenticated and role-gated.
- Confirm backups can be created and restore can be tested safely.
- Confirm documentation matches the repository as implemented.
- Confirm known limitations are explicit before go-live.

The MVP is accepted only for controlled self-hosted operation by trusted operators. It is not accepted as a public social network, public registration service, open federation service, or fully packaged production SaaS product.

## 2. Definition of "MVP Complete"

MVP complete means the repository contains a coherent first deployment that an operator can configure, start, validate, back up, and document with fake or approved staging data.

MVP complete requires:

- Docker Compose renders valid configuration with a reviewed `.env`.
- Caddy routes public HTTP and HTTPS service hostnames to internal upstream services.
- PostgreSQL stores portal identity and access data.
- Portal migrations apply cleanly.
- Portal workflows support invites, manual verification, room access, Jitsi meeting token issuance, and audit records.
- Basic admin UI can view the implemented administrative data.
- Prosody is configured with registration disabled and federation disabled.
- Converse.js is served through the reverse proxy and points at Prosody browser transports.
- Jitsi web is routed through the reverse proxy and requires JWT authentication.
- Backup scripts create local backups for the current data stores and configurations.
- Documentation explains setup, operation, security defaults, backup, restore, and known limits.

MVP complete does not require automated Prosody account provisioning, production portal packaging, native mobile apps, Tor access, library integration, IRC fallback, open federation, public registration, SMTP delivery, or advanced moderation tooling.

## 3. Required Features Checklist

### Invite-Only Registration

Acceptance criteria:

- Admins can create invites.
- Invites record creator, status, expiry, reusable state, and redemption state.
- Invites can be listed.
- Invites can be revoked.
- Valid invites can be redeemed.
- Expired invites are rejected.
- Revoked invites are rejected.
- Already-used single-use invites are rejected.
- Reusable invites are explicit.
- Invite redemption creates a limited portal user state.
- Invite creation, revocation, and redemption create audit events.
- No public self-registration path is enabled.

### Manual Verification

Acceptance criteria:

- Users can submit verification requests for `clergy`, `monastic`, and `parish_admin`.
- Admins can view pending verification requests.
- Admins can approve verification requests.
- Admins can reject verification requests with a reason.
- Approved requests assign the correct role.
- Rejected requests do not assign privileged roles.
- Users cannot approve their own verification.
- Verification decisions are tied to an admin user.
- Verification request creation, approval, and rejection create audit events.

### Role-Based Room Access

Acceptance criteria:

- Portal can define rooms or channels.
- Supported room scopes are present:
	- `public_to_members`
	- `group_only`
	- `clergy_only`
	- `monastic_only`
	- `admin_only`
	- `invite_only`
- Portal can calculate whether a user may access a room.
- Access decisions consider account state, roles, group membership, explicit room membership, and suspension state where implemented.
- Room membership records are created only when access rules allow it.
- Room creation, access changes, and membership changes create audit events.
- Private room access remains portal-controlled.

### Web Chat (Converse)

Acceptance criteria:

- Converse.js frontend files are present under `converse/`.
- Converse.js is routed through the reverse proxy under `CHAT_DOMAIN`.
- Converse.js configuration uses environment-driven XMPP connection URLs.
- Browser WebSocket or BOSH paths point to Prosody through the reverse proxy.
- Public registration remains disabled in the chat path.
- The chat UI is minimal and suitable as the first web chat surface.

### Prosody Messaging Working

Acceptance criteria:

- `prosody/prosody.cfg.lua` exists and renders a minimal valid Prosody configuration for the MVP.
- `XMPP_DOMAIN`, `XMPP_ADMIN_JID`, `XMPP_MUC_DOMAIN`, and registration settings are environment-driven.
- `XMPP_REGISTRATION_ENABLED=false` is required.
- Prosody public registration is disabled.
- Prosody federation is disabled for MVP.
- Prosody browser transports are available internally for Caddy routing.
- MUC or groupchat configuration is present for the current chat foundation.
- Prosody data is mounted persistently by Docker Compose.
- Prosody admin interfaces are not exposed publicly.

Manual account creation or operator provisioning is acceptable for MVP validation because portal-to-Prosody provisioning is not implemented yet.

### Jitsi Authenticated Meetings

Acceptance criteria:

- Jitsi web service is routed through the reverse proxy under `MEET_DOMAIN`.
- Jitsi JWT environment variables are present in `.env.example` as placeholders.
- JWT authentication is enabled.
- Empty or missing JWT secrets are rejected by configuration or validation.
- Anonymous public room creation remains disabled.
- Portal can create meeting records for allowed users.
- Portal can issue meeting tokens for allowed users.
- Portal can issue guest tokens only where explicit guest access is allowed.
- Meeting creation and token issuance create audit events.
- Meeting names alone do not grant access.

### Basic Admin UI

Acceptance criteria:

- Admin UI can view users.
- Admin UI can view groups or parishes.
- Admin UI can view roles.
- Admin UI can manage invites at the implemented level.
- Admin UI can review verification requests.
- Admin UI can approve or reject verification requests.
- Admin UI can view rooms or channels.
- Admin UI can view audit events.
- Privileged actions require an approved admin role.
- Ordinary users cannot access admin-only functions.

### Backups Functioning

Acceptance criteria:

- `scripts/backup.sh` exists and loads `.env`.
- `scripts/restore.sh` exists and loads `.env`.
- `scripts/list-backups.sh` exists if present in the current backup tooling.
- Backup output goes under the configured local backup path.
- Backup output is timestamped.
- PostgreSQL portal data is backed up.
- Prosody data and config are backed up.
- Jitsi config and data are backed up when present.
- Reverse proxy data is backed up where managed by the stack.
- Backup output is excluded from Git.
- Restore script has safety checks before replacing data.
- Restore is validated only with disposable or approved test data before production go-live.

## 4. Security Criteria

Security acceptance requires:

- `.env` is not tracked by Git.
- `.env.example` contains placeholders only.
- No real secrets are committed.
- No real invite tokens are committed.
- No real JWT secrets or token bodies are committed.
- No real user data is committed.
- No production logs or backups are committed.
- Public registration remains disabled.
- Open federation remains disabled.
- Internal PostgreSQL, Prosody, Converse.js, portal, and Jitsi service ports remain private except required public media transport.
- Reverse proxy security headers remain configured where compatible with each service.
- Portal admin routes require admin roles.
- Users cannot self-assign privileged roles.
- Verification decisions require an admin user.
- Jitsi room creation remains authenticated and role-gated.
- Backup manifests do not print secret values.
- Logs avoid passwords, session cookies, invite tokens, recovery tokens, JWT bodies, and private message content.

## 5. Usability Criteria

Usability acceptance requires:

- README setup instructions are clear enough for a technical operator to follow.
- First-time user flows remain invite-only and plain-language where implemented.
- Admin views expose the data needed for MVP operation without requiring direct database inspection for routine tasks.
- Invite status, verification status, room scope, meeting status, and audit events are understandable to an administrator.
- Error states for expired, revoked, or used invites are clear.
- Ordinary users are not shown internal service names, stack traces, raw JWTs, or database errors.
- Chat entry uses the configured chat hostname.
- Meeting entry uses portal-issued or controlled Jitsi links.
- Mobile browser use is not blocked by obvious layout or routing defects in the implemented portal and chat surfaces.

## 6. Performance Criteria

Performance acceptance is modest for MVP.

Criteria:

- The stack is suitable for small parish, monastic, or group testing on a single host.
- Docker Compose starts the required services without repeated crash loops under normal test configuration.
- Portal CLI and admin views respond adequately with small test datasets.
- PostgreSQL migrations complete on disposable MVP data.
- Converse.js frontend loads through Caddy without excessive assets or external build steps.
- Prosody browser transports remain available for normal test chat use.
- Jitsi supports a small test meeting after JWT authentication is configured.
- Backup scripts complete in a reasonable time for small MVP datasets.

Large meetings, multi-parish scale, federation load, library storage growth, and stress-tested capacity are not MVP acceptance requirements.

## 7. Failure Handling Criteria

Failure handling acceptance requires:

- Missing required environment variables fail clearly or prevent unsafe startup where implemented.
- Invalid registration settings do not enable Prosody public registration.
- Expired, revoked, and already-used invites fail closed.
- Unauthorized verification decisions fail closed.
- Unauthorized room membership creation fails closed.
- Unauthorized meeting creation and token issuance fail closed.
- Reverse proxy upstream failures do not expose internal services.
- Backup script failures return non-zero status.
- Restore script refuses unsafe restores without the required confirmation.
- Operators can stop or disable affected services without deleting portal data, Prosody data, Jitsi state, backups, or audit records.

## 8. Documentation Completeness Criteria

Documentation acceptance requires:

- README explains project purpose, requirements, setup, environment variables, development use, production notes, backup and restore, and security notes.
- `docs/` includes architecture, identity and verification, deployment, security model, MVP status, and operational design notes.
- `.env.example` remains aligned with documented variables.
- Future features are clearly marked as future, planned, deferred, or design-only.
- Implemented features are not overstated.
- Local development domains are examples only.
- Production TLS guidance uses Caddy and Let's Encrypt without committing certificates.
- Backup and restore guidance matches the local filesystem backup scripts.
- Known limitations are visible before deployment.

## 9. Test Completion Criteria

MVP test completion requires a dated validation record from the operator or reviewer covering:

- Worktree state checked.
- `.env.example` reviewed for placeholders.
- Compose configuration rendered.
- Portal migrations applied against disposable or staging data.
- Invite workflow tested with fake data.
- Verification workflow tested with fake data.
- Room access workflow tested with fake data.
- Admin UI opened and reviewed.
- Converse.js route opened.
- Prosody browser transport path checked.
- Jitsi route opened.
- Jitsi meeting token issued for an allowed fake user.
- Unauthorized Jitsi creation denied.
- Backup script completed.
- Restore script tested against disposable data.
- Security checks reviewed.
- Documentation reviewed against current behavior.

Suggested commands:

```bash
git status --short
docker compose --env-file .env config
python3 -m portal.app.cli migrate
scripts/backup.sh
scripts/list-backups.sh
```

Restore validation should be performed only against disposable data unless the operator is running an approved recovery procedure.

## 10. Known Acceptable Limitations

The following limitations are acceptable for MVP:

- Portal is not packaged as a production web image.
- Portal CLI and admin UI run from the repository with a Python virtual environment.
- Prosody account provisioning is not automated by the portal.
- Portal room policy is not fully synchronized into Prosody MUC state.
- Email delivery for invites is not implemented.
- Account recovery is not complete.
- Native mobile app support is not implemented.
- Native XMPP client support is not formally validated.
- End-to-end encryption is not claimed as a platform-wide guarantee.
- Library integration is not implemented.
- Tor onion access is not implemented.
- IRC fallback and bridges are not implemented.
- Trusted federation is design-only and not enabled.
- Advanced moderation and abuse reporting tooling are not implemented.
- External monitoring and alerting services are not implemented.
- Performance has not been stress-tested for large meetings or large communities.

These limitations must be accepted by the operator before go-live with real users.

## 11. Final Review Process

Final MVP review should be done by a trusted operator or maintainer before real community data is used.

Review steps:

1. Confirm the repository matches the intended release commit.
2. Confirm no unreviewed local changes are present.
3. Confirm `.env` values are operator-owned and not committed.
4. Confirm required domains and DNS are controlled by the operator.
5. Confirm Caddy can obtain or manage valid TLS certificates for production hostnames.
6. Confirm all required MVP services start.
7. Confirm route checks pass for portal, chat, XMPP browser transports, and Jitsi.
8. Confirm invite, verification, room, meeting, admin UI, and audit checks pass with fake data.
9. Confirm backup and restore checks pass.
10. Confirm security criteria pass.
11. Confirm documentation matches the deployed behavior.
12. Confirm known limitations are accepted.
13. Record the final decision in operator notes.

Review should stop if public registration, open federation, unauthenticated meeting creation, exposed internal ports, missing backups, or undocumented secrets are found.

## 12. Go-Live Decision Criteria

Go-live may proceed only when:

- Final review has passed.
- Production `.env` exists outside Git.
- Strong secrets have been generated outside Git.
- DNS points to the intended host.
- TLS is working for public routes.
- Public registration is disabled.
- Open federation is disabled.
- Jitsi authentication is enabled.
- Admin roles are limited to trusted operators.
- Backup has completed.
- Restore has been tested against disposable or approved data.
- Operator emergency contacts exist outside the repository.
- Known MVP limitations have been accepted.
- A rollback path has been selected before inviting real users.

Go-live should not proceed if the operator cannot restore portal data, cannot verify admin access, cannot issue authenticated meeting access, or cannot confirm that public registration and open federation remain disabled.

## 13. Rollback Plan

Rollback must preserve trust records and avoid silent data loss.

Rollback steps:

1. Stop inviting new users.
2. Disable affected public routes or services if exposure is possible.
3. Preserve current logs, audit events, backup manifests, and operator notes.
4. Identify the last known-good commit, `.env`, backup, and service configuration.
5. Restore the last known-good configuration or backup in a disposable target first where practical.
6. Restore production only after identity, roles, verification, rooms, meetings, and audit events pass review.
7. Rotate secrets if exposure is suspected.
8. Confirm public registration remains disabled.
9. Confirm open federation remains disabled.
10. Confirm Jitsi authentication remains enabled.
11. Confirm admin routes remain role-gated.
12. Confirm internal service ports remain private.
13. Confirm backups still run after rollback.
14. Notify approved administrators before notifying ordinary users.
15. Record the rollback result.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, reverse proxy data, backups, or unrelated service configuration.
