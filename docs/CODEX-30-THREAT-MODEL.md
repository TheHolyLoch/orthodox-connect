# Orthodox Connect Threat Model

## 1. Threat Model Goals

The threat model defines what Orthodox Connect must protect, where the trust boundaries are, and which risks remain after the current MVP controls are applied.

Goals:

- Protect invite-only, manually verified community access.
- Protect clergy, monastic, parish admin, diocesan admin, and platform admin identity from impersonation.
- Protect portal identity, roles, groups, rooms, meetings, and audit records.
- Protect chat, meeting, backup, configuration, and log metadata from avoidable exposure.
- Keep public registration disabled.
- Keep open federation disabled unless a later trusted federation plan explicitly enables it.
- Keep internal services private behind the reverse proxy.
- Make risks clear for parish, diocesan, monastic, and technical operators.
- Avoid claiming stronger privacy or end-to-end security than the selected services and clients provide.

This document is a design document only. It does not implement security changes.

## 2. Assets to Protect

Protected assets:

| Asset                     | Sensitivity | Notes |
| ------------------------- | ----------- | ----- |
| Portal user records       | High        | Account state, display names, roles, groups, verification state, rooms, meetings, and audit references. |
| Verification records      | High        | Clergy, monastic, and parish admin requests and decisions. |
| Admin accounts            | High        | Can create invites, approve verification, manage access, issue meetings, and review audit events. |
| Invite records            | High        | Invite tokens are not stored raw, but invite state and scope reveal trust workflow data. |
| Room and group membership | High        | Can reveal parish, monastery, ministry, clergy, admin, or private participation. |
| Meeting records           | High        | Meeting names, access, guest records, and token issuance metadata reveal activity. |
| Jitsi JWT secrets         | High        | Compromise can allow forged meeting access until rotated. |
| PostgreSQL data           | High        | Source of truth for portal identity, policy, and audit records. |
| Prosody data              | High        | XMPP accounts, rooms, and possible message archive data. |
| Reverse proxy data        | High        | ACME account data, certificates, and routing state. |
| Backups                   | High        | Can contain portal, Prosody, Jitsi, reverse proxy, and configuration data. |
| `.env` values             | High        | Database passwords, JWT secrets, portal secrets, hostnames, and backup paths. |
| Logs                      | Medium to high | Can expose usernames, IP addresses, room names, meeting names, errors, and admin actions. |
| Public hostnames          | Medium      | Can expose deployment shape and community service locations. |

Secrets, raw tokens, private keys, real user data, backups, and production logs must not be committed to Git.

## 3. Trust Boundaries

Primary trust boundaries:

- Public internet to Caddy reverse proxy.
- Reverse proxy to internal Docker services.
- Portal to PostgreSQL.
- Portal to Jitsi token issuance.
- Converse.js browser client to Prosody browser transports.
- Prosody XMPP service to stored XMPP data.
- Jitsi web and media services to authenticated users and guests.
- Local backup scripts to backup output paths.
- Operator-controlled `.env` and secrets outside Git.
- Admin UI and CLI workflows to portal database state.

Boundary rules:

- Caddy is the only public HTTP and HTTPS entrypoint.
- PostgreSQL must remain internal.
- Prosody native and admin interfaces must not be exposed publicly.
- Jitsi internal Prosody, Jicofo, and control services must remain internal.
- Jitsi JVB media port is public only where required for media transport.
- Browser XMPP traffic should route through HTTPS or WSS paths.
- Portal policy is the source of truth for user state, room access, roles, meetings, and audit records.
- Prosody and Jitsi state must not override portal decisions.
- Backups and restore targets must be treated as sensitive environments.

## 4. Adversary Types

### Casual Abuse

Casual abuse includes spam, nuisance accounts, leaked invite links, low-effort probing, repeated failed logins, and attempts to join rooms or meetings without permission.

Controls:

- Invite-only onboarding.
- Expiring and revocable invites.
- Single-use invites by default.
- Disabled public XMPP registration.
- Disabled open federation.
- Role-gated meeting creation.
- Audit records for access decisions.
- Future rate limits for login, invite redemption, and meeting token issuance.

### Impersonation

Impersonation includes attempts to appear as clergy, monastic, parish admin, diocesan admin, platform admin, official parish accounts, or known members.

Controls:

- Manual verification for clergy, monastic, and parish admin status.
- Users cannot self-assign privileged roles.
- Visible verified labels must come from portal state.
- Admin role assignment is audited.
- Room and meeting access derive from portal roles and groups.
- IRC names, chat nicknames, Jitsi display names, and external clients are not proof of verified status.

### Targeted Harassment

Targeted harassment includes repeated unwanted contact, disruptive room behavior, invite misuse, meeting disruption, sharing private content outside a room, and attempts to pressure admins or users.

Controls:

- Admin-scoped review of users, rooms, invites, meetings, and audit events.
- Suspension model for account-level safety.
- Room membership removal and access changes.
- Meeting guest approval and revocation.
- Future abuse reporting and moderation tooling.
- Short, scoped evidence retention where moderation policy allows it.

### State-Level Censorship

State-level censorship includes DNS blocking, IP blocking, TLS interference, hosting pressure, traffic disruption, domain seizure, or throttling of public endpoints.

Controls:

- Self-hosted deployment model.
- Operator-controlled DNS and TLS.
- Backup and restore support for host migration.
- Disaster recovery runbooks.
- Future Tor onion access design.
- Future IRC fallback design for low-trust emergency notices.

Limits:

- The MVP does not hide that users connect to the public service.
- Jitsi over Tor is not promised.
- Server operators and hosting providers can still see infrastructure metadata.

### Insider Threats

Insider threats include malicious or careless admins, compromised admin accounts, operators mishandling backups, accidental secret leakage, and incorrect verification or room access decisions.

Controls:

- Admin actions require approved roles.
- Privileged actions create audit events.
- Admin authority should be scoped by group or role.
- Backups and logs are treated as sensitive.
- `.env` and secrets stay outside Git.
- Admin accounts should not be shared.
- Stronger recovery and review are expected for privileged roles.

Limits:

- Platform admins and technical operators remain trusted with server-side metadata.
- The MVP does not yet implement all future controls such as MFA, full recovery hardening, or automated drift reconciliation.

## 5. Attack Surfaces

### Portal

Portal risks:

- Weak or compromised portal credentials.
- Missing authorization checks on admin routes.
- Invite redemption abuse.
- Role or verification self-assignment bugs.
- Raw token exposure in logs or URLs.
- SQL errors, stack traces, or internal hostnames exposed to users.
- Bad migrations or data repair changing trust records.

Controls:

- Admin routes require approved admin roles.
- Invite redemption rejects expired, revoked, and already-used single-use invites.
- Verification decisions require admin users.
- Meeting creation and token issuance are role-gated.
- Audit events record trust and access decisions.
- Errors should avoid stack traces, SQL details, raw tokens, and secrets.
- PostgreSQL remains internal.

### XMPP and Prosody

XMPP and Prosody risks:

- Public registration accidentally enabled.
- Open federation accidentally enabled.
- Native XMPP ports exposed without policy review.
- Admin interfaces exposed publicly.
- Prosody account state drifting from portal state.
- Room names, membership, presence, or message archive data exposed.
- Message bodies stored where users expect no archive.

Controls:

- `XMPP_REGISTRATION_ENABLED=false`.
- Prosody public registration disabled.
- Prosody federation disabled for MVP.
- Browser XMPP transport routed through Caddy.
- Internal Prosody ports are not published.
- Room creation restricted.
- Portal room policy remains source of truth.
- Message archive and OMEMO limitations must be explained honestly.

### Web Chat

Web chat risks:

- Browser client exposing login or room metadata.
- Misconfigured WebSocket or BOSH URL.
- External XMPP clients hiding verification labels.
- Users mistaking chat display names for verified status.
- Browser storage or device compromise exposing account access.

Controls:

- Converse.js connects through environment-configured WebSocket or BOSH URLs.
- Browser XMPP routes use reverse proxy paths.
- Verification status must come from portal data.
- Public registration remains disabled.
- Mobile and external client guidance should explain OMEMO and verification limits.

### Jitsi

Jitsi risks:

- Anonymous public room creation.
- Forged or leaked JWTs.
- Meeting links forwarded outside approved participants.
- Guest access that does not expire.
- Meeting names granting access by themselves.
- Jitsi internal services exposed publicly.
- Heavy media load affecting service availability.

Controls:

- Jitsi JWT authentication is enabled.
- Empty JWT variables are rejected.
- Meeting creation is role-gated.
- Guests require explicit approval.
- Token issuance metadata is recorded without storing token bodies.
- Jitsi internal Prosody and control services remain private.
- Only the required media transport port is public.

### Reverse Proxy

Reverse proxy risks:

- Public routes exposing internal services.
- Incorrect upstreams bypassing portal policy.
- Missing WebSocket routing.
- Logging sensitive query strings.
- TLS renewal failure.
- Security headers missing or incompatible.
- Accidental route for disabled future services.

Controls:

- Caddy is the only public HTTP and HTTPS entrypoint.
- Routes use internal Docker service names.
- PostgreSQL, Prosody admin interfaces, and Jitsi internals are not routed publicly.
- Security headers are configured where compatible.
- Library route remains a placeholder until implemented.
- TLS certificates are managed by Caddy, not committed manually.

### Backups

Backup risks:

- Backups committed to Git.
- Backup archives stored on the same failed host only.
- Backup manifests leaking secrets.
- Restore from stale or untrusted data.
- Production backups loaded into local development.
- Untested backups giving false confidence.
- Backups retaining deleted or sensitive data longer than expected.

Controls:

- Backup output is excluded from Git.
- Backup scripts load `.env` and avoid printing secret values.
- Backups include PostgreSQL, Prosody, Jitsi, and reverse proxy data where present.
- Restore scripts include basic safety checks.
- Restore tests should use disposable or approved data.
- Production data must not be copied into lower environments unless scrubbed and approved.

## 6. Impersonation Risks and Controls

Risks:

- User chooses a display name that looks like clergy, monastic, parish admin, diocesan admin, platform admin, or an official parish account.
- User claims status in chat, meetings, or external clients before verification.
- Remote or bridged identities are mistaken for local verified users.
- Compromised verified accounts continue to appear trusted.
- Jitsi names or chat nicknames are treated as identity proof.

Controls:

- Verified status comes only from portal roles and verification decisions.
- Users cannot self-approve verification requests.
- Admins cannot rely on display names as proof of role.
- Verification decisions are tied to an admin user and audited.
- Suspended users should lose active verified status.
- Trusted federation, IRC bridge, and external client support must visibly distinguish remote or bridged identities if implemented later.
- Official names and role-like names should be reserved or reviewed when account policy supports it.

## 7. Account Takeover Risks and Controls

Risks:

- Weak passwords.
- Reused passwords.
- Phishing of portal or XMPP credentials.
- Session cookie theft.
- Compromised administrator account.
- Account recovery bypassing suspension or verification.
- Stolen device with saved browser or chat session.
- Prosody credentials remaining active after portal suspension.

Controls:

- Strong password requirements are needed when full login is implemented.
- Admin accounts should have stricter session and recovery requirements.
- Account recovery must not bypass suspension or verification.
- Suspended users must lose portal, chat, room, and meeting access.
- Jitsi tokens should be short-lived.
- Admin accounts should not be shared.
- Future MFA is strongly preferred for privileged roles.
- Provisioning sync must disable Prosody access when portal state is suspended or disabled.

## 8. Data Leakage Risks and Controls

Risks:

- Message bodies, room names, membership, meeting names, and presence metadata exposed through logs, backups, or misconfigured clients.
- Invite tokens, JWTs, recovery tokens, session cookies, or `.env` values printed in logs.
- Production database dumps copied into local or staging environments.
- Reverse proxy logs storing sensitive query strings.
- Debug logging left enabled.
- Admin notes containing pastoral or private content.
- Screenshots or support output containing private data.

Controls:

- Do not log passwords, session cookies, JWT bodies, invite tokens, recovery tokens, message bodies, full request bodies, or `.env` contents.
- Keep debug logging off by default in production.
- Keep retention short unless policy requires longer.
- Treat logs and backups as sensitive records.
- Store production secrets outside Git.
- Use fake data in local development and staging.
- Avoid private pastoral notes in portal records.
- Review message archive settings before production use.

## 9. Denial-of-Service Risks and Controls

Risks:

- HTTP request floods against portal, chat, or meeting routes.
- Repeated invite redemption attempts.
- Repeated login attempts.
- Jitsi media load exhausting CPU, memory, or bandwidth.
- Disk full from logs, backups, uploads, or database growth.
- PostgreSQL unavailable.
- Prosody or Jitsi component crashes.
- Caddy TLS renewal failures.

Controls:

- Keep public host ports limited.
- Add rate limits in future for login, invite redemption, recovery, and meeting token issuance.
- Keep reusable invites rare and expiring.
- Monitor disk usage, backup size, and container health.
- Keep Jitsi deployment sized for expected use.
- Keep backup and restore procedures tested.
- Use operational checks for reverse proxy, PostgreSQL, Prosody, Jitsi, and portal.
- Fail closed when policy checks cannot be completed.

## 10. Censorship and Interference Risks and Controls

Risks:

- DNS blocking or registrar account loss.
- Public IP blocking.
- TLS interception or certificate problems.
- Hosting provider pressure or outage.
- Network throttling of Jitsi media.
- Users unable to reach public hostnames.
- Emergency communications moving to untrusted channels.

Controls:

- Keep operator-controlled DNS and TLS.
- Keep backups and `.env` recovery material outside the production host.
- Use disaster recovery restore order before public user notice.
- Avoid temporary unreviewed domains or IP-only access for ordinary users.
- Future Tor onion access may support portal and chat.
- Future IRC fallback may support low-trust emergency notices only.
- Do not use fallback channels to approve users, verify clergy or monastics, or bypass portal audit records.

## 11. Misconfiguration Risks

Misconfiguration risks:

- `XMPP_REGISTRATION_ENABLED` set to true.
- Prosody `s2s` or federation enabled without trusted federation review.
- Jitsi guest or anonymous room creation enabled.
- Internal service ports published by mistake.
- Real domains or secrets committed to Git.
- Production `.env` reused in staging or local development.
- Backup paths pointed inside the repository.
- Caddy routes exposing internal services.
- Reverse proxy routes logging sensitive query strings.
- Portal database pointed at the wrong environment.
- Jitsi JWT variables missing, weak, or reused across environments.

Controls:

- Keep `.env.example` as a template only.
- Keep `.env` out of Git.
- Use environment-specific secrets and data.
- Check `docker compose config` before deployment.
- Confirm public registration remains disabled after changes.
- Confirm federation remains disabled after changes.
- Confirm Jitsi authentication remains enabled after changes.
- Confirm internal ports remain private after changes.
- Test backups and restores with disposable or approved data.

## 12. Residual Risks

Residual risks that remain after current MVP controls:

- Server operators can access server-side metadata.
- Hosting providers can observe infrastructure metadata.
- XMPP and Jitsi metadata can reveal communication patterns.
- Message archive behavior depends on Prosody modules and room settings.
- OMEMO support depends on client behavior and is not platform-wide.
- External XMPP clients may not display portal verification status.
- Account recovery, MFA, rate limiting, and full login hardening are not complete.
- Prosody account provisioning and room sync are not automated.
- Admin mistakes can still grant incorrect roles or room access.
- Backups can retain data after user-facing deletion or suspension.
- Censorship resistance is limited until Tor or other reviewed fallback paths exist.

Operators should explain these limits plainly before production use.

## 13. Assumptions

Assumptions:

- Orthodox Connect is deployed as a private, invite-only instance.
- Public registration remains disabled.
- Open federation remains disabled.
- The operator controls DNS, TLS, host access, backups, and `.env` storage.
- Caddy is the public HTTP and HTTPS entrypoint.
- PostgreSQL, Prosody internals, and Jitsi internal services remain private.
- Portal database state is the source of truth for roles, rooms, meetings, and audit records.
- Admins and technical operators are trusted with server-side metadata.
- Users and admins use supported browsers or reviewed clients.
- Local development and staging use fake or scrubbed data.
- No real secrets, domains, backups, logs, or user data are committed.
- Future Tor, federation, IRC, bridge, and library features require separate implementation review before enablement.

If any assumption changes, the threat model should be reviewed before production deployment continues.

## 14. Rollback Plan

Threat model rollback means returning to the last known-safe trust and exposure boundary after a security mistake or unsafe configuration change.

Rollback steps:

1. Stop affected public routes or services if current exposure is unsafe.
2. Preserve portal data, audit events, logs, and backup manifests for review.
3. Revert the unsafe configuration, route, role, invite, room, meeting, or token behavior.
4. Confirm public registration remains disabled.
5. Confirm open federation remains disabled.
6. Confirm Jitsi authentication remains enabled.
7. Confirm admin routes require approved admin roles.
8. Confirm internal service ports remain private.
9. Revoke unsafe invites, meeting access, guest records, room memberships, or role assignments.
10. Suspend compromised accounts where needed.
11. Rotate exposed or suspected secrets.
12. Restore from backup only if data integrity cannot be repaired safely.
13. Add corrective audit events or operator notes.
14. Re-run deployment validation before reopening affected routes.

Rollback must not delete users, groups, roles, invites, verification records, rooms, meetings, audit events, backups, Prosody data, Jitsi state, reverse proxy data, or unrelated service configuration.
