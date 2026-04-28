# Orthodox Connect Jitsi Design

## 1. Jitsi Goals

Jitsi provides authenticated video meetings for approved Orthodox Connect users and explicitly approved guests.

Goals:

- Support parish, group, clergy, monastic, and administrative video meetings.
- Keep meeting creation role-gated.
- Keep anonymous public room creation disabled.
- Tie meeting access to portal users, room access, group membership, verified roles, or explicit guest approval.
- Use JWT authentication for Jitsi access.
- Keep meeting names from granting access by themselves.
- Record meeting creation and token issuance in portal audit events.
- Avoid storing JWT token bodies, passwords, or private participant notes in logs.
- Keep Jitsi configuration and generated state out of Git.

Jitsi should remain a meeting layer, not a replacement for portal identity, room policy, or verification.

## 2. Jitsi Role in the Platform

Jitsi Meet is the video service for Orthodox Connect.

Jitsi responsibilities:

- Serve the browser meeting interface.
- Validate JWT access tokens.
- Host active video rooms.
- Connect Jitsi web, Jicofo, JVB, and internal Jitsi Prosody components.
- Handle live audio, video, screen sharing, and meeting presence.

Portal responsibilities:

- Decide who may create official meetings.
- Decide who may join a meeting.
- Create meeting records.
- Issue meeting links and JWTs.
- Approve or revoke guest access.
- Record audit events for meeting creation and token issuance.

Current Compose services:

| Service          | Role |
| ---------------- | ---- |
| `jitsi-web`      | Browser-facing Jitsi Meet web app behind Caddy. |
| `jitsi-prosody`  | Internal Jitsi XMPP service for meeting auth and control. |
| `jitsi-jicofo`   | Jitsi conference focus service. |
| `jitsi-jvb`      | Jitsi video bridge for media transport. |

The main Orthodox Connect Prosody service is separate from Jitsi's internal Prosody service.

## 3. Meeting Types

Meeting types should be explicit in portal data and user interface.

| Meeting Type               | Purpose | Default Creation Policy |
| -------------------------- | ------- | ----------------------- |
| `private`                  | Named user or invite-only meeting. | Approved meeting creator roles only. |
| `group`                    | Meeting tied to a parish, monastery, ministry, mission, or group. | Group-scoped administrators or approved creator roles. |
| `clergy_only`              | Meeting for verified clergy. | Approved clergy or admin roles, with local policy review. |
| `admin`                    | Administrator coordination meeting. | Parish, diocesan, or platform admins by scope. |
| `public_event_placeholder` | Later placeholder for controlled public-facing events. | Disabled until separately designed. |

Rules:

- `public_event_placeholder` is not public access and must not enable anonymous room creation.
- Sensitive meeting names should avoid exposing pastoral, clergy, monastic, youth, or private details.
- Meeting type must not override suspension or disabled account state.
- Meeting type must not grant access without a portal policy check.

## 4. Authentication Model

Jitsi authentication uses JWT.

Current configuration direction:

- `AUTH_TYPE=jwt`.
- `ENABLE_AUTH=1`.
- `ENABLE_GUESTS=0`.
- `JWT_ALLOW_EMPTY=0`.
- Jitsi web is routed through the reverse proxy.
- Jitsi internal services stay on the internal video network.

Authentication rules:

- Anonymous users must not create rooms.
- Meeting links alone must not grant access.
- Portal users must be approved and not suspended.
- Meeting creators must have an approved creator role.
- Guests must have explicit guest records or equivalent portal approval.
- Token issuance must happen only after portal policy checks.

Authentication must not depend on users connecting directly to Jitsi internals, PostgreSQL, Prosody internals, or Docker services.

## 5. JWT Token Model

JWTs are short-lived meeting access tokens issued by the portal after access checks.

Current environment variables:

| Variable                      | Purpose |
| ----------------------------- | ------- |
| `JITSI_JWT_APP_ID`            | Accepted issuer and audience value. |
| `JITSI_JWT_APP_SECRET`        | Shared signing secret. |
| `JITSI_TOKEN_TTL_SECONDS`     | Default token lifetime. |
| `JITSI_PUBLIC_URL`            | Public meeting URL base. |
| `JITSI_MEETING_CREATOR_ROLES` | Roles allowed to create official meetings. |

Token requirements:

- Include enough claims for Jitsi to validate issuer, audience, room, subject, and expiry.
- Use short expiry.
- Be issued for one meeting or room context.
- Be issued only to an approved user or approved guest.
- Not be stored in full after issuance.
- Not be logged.
- Not be placed in public docs, screenshots, or support requests.

Portal records:

- `meetings` stores meeting records.
- `meeting_guests` stores approved guest metadata where guests are allowed.
- `meeting_token_issuances` stores token issuance metadata and token IDs, not token bodies.
- `audit_events` records meeting creation and token issuance.

Secret rotation:

- Rotating `JITSI_JWT_APP_SECRET` should invalidate old tokens.
- After rotation, issue new tokens only after portal checks.
- Rotate the JWT secret if token bodies, signing secrets, `.env`, or backup secrets are exposed.

## 6. Room Creation Policy

Jitsi room creation must be controlled by the portal.

Creator roles:

- `parish_admin`
- `diocesan_admin`
- `platform_admin`
- `clergy_verified`, where local policy allows it

Rules:

- Public anonymous room creation remains disabled.
- Users cannot create official meetings unless their role is listed in `JITSI_MEETING_CREATOR_ROLES`.
- Group-scoped admins may create meetings only inside their approved group scope.
- Clergy-only meeting creation should require `clergy_verified` plus any local scope checks.
- Meeting names must be generated or approved by the portal.
- Meeting creation must create an audit event.
- Suspended or disabled users cannot create meetings.

Room creation should fail closed if role, group, JWT, or configuration checks are unclear.

## 7. Guest Access Policy

Guest access is explicit and limited.

Rules:

- `JITSI_ENABLE_GUESTS=0` remains the MVP default.
- Guests may join only through portal-approved guest access.
- Guests must not create rooms.
- Guest access must have an expiry.
- Guest access should be tied to a specific meeting.
- Guest display names should be required.
- Guest tokens must be short-lived.
- Guest token issuance must create an audit event.
- Guest records must be revocable.

Guest access should be used for cases such as a visiting speaker, approved remote participant, or limited pastoral meeting participant. It must not become public registration.

## 8. Moderator Policy

Moderator rights should be assigned intentionally.

Moderator candidates:

- Meeting creator.
- Approved group administrator.
- Parish administrator for a parish-scoped meeting.
- Diocesan administrator for a diocesan-scoped meeting.
- Platform administrator for emergency or technical cases.
- Explicitly assigned moderator for a meeting.

Rules:

- Guests are not moderators by default.
- Moderator status must not come from a display name.
- Moderator status should be derived from portal role and meeting scope.
- Sensitive meetings should have at least one accountable approved moderator.
- Moderator assignment should be visible to administrators.
- Moderator changes should be auditable where the portal controls them.

Future implementation should decide how portal moderator policy maps to Jitsi moderator claims and room behavior.

## 9. Recording Policy

Recording is disabled by default.

Rules:

- Do not enable recordings until storage, consent, retention, access control, and backup policy are reviewed.
- Do not record clergy, monastic, pastoral, youth, or private meetings by default.
- If recordings are enabled later, access must be role-gated and audited.
- Recording storage must not be committed to Git.
- Recording files must be backed up only under a reviewed retention policy.
- Users should be clearly informed when recording is active.

The current MVP design should assume no recording service and no recording workflow.

## 10. Lobby and Waiting Room Policy

Lobby or waiting room features are recommended for sensitive meetings where Jitsi support and configuration allow them.

Policy:

- Clergy-only, monastic, admin, pastoral, or guest-enabled meetings should prefer lobby or explicit admission.
- A moderator should admit waiting participants.
- Guest access should not bypass lobby policy where lobby is enabled.
- Lobby decisions should not replace portal access checks.
- Lobby use should be tested before production reliance.

If lobby behavior is not configured or tested, meeting access should rely on stricter token issuance and shorter token expiry.

## 11. Meeting Link Lifecycle

Meeting links should be controlled records, not permanent public URLs.

Lifecycle:

1. Approved creator requests a meeting.
2. Portal creates a `meetings` record.
3. Portal generates or stores the Jitsi room name.
4. Portal issues links or tokens only to allowed users or guests.
5. Tokens expire after `JITSI_TOKEN_TTL_SECONDS` or a meeting-specific policy.
6. Meeting may be closed or cancelled.
7. Closed or cancelled meetings stop receiving new tokens.
8. Guest records can expire or be revoked.
9. Audit events preserve creation and token issuance history.

Rules:

- Meeting names must not grant access by themselves.
- Old links should fail when tokens expire or secrets rotate.
- Cancelled meetings should stop token issuance.
- Meeting slugs should avoid sensitive real-world details.
- Meeting links must not be committed to Git or public docs.

## 12. Portal Integration Points

The portal is the control plane for Jitsi access.

Current portal data:

- `meetings`
- `meeting_guests`
- `meeting_token_issuances`
- `users`
- `roles`
- `user_roles`
- `groups`
- `group_memberships`
- `rooms`
- `room_memberships`
- `audit_events`

Required integration points:

- Create meeting.
- List meetings for allowed users and administrators.
- Check creator role.
- Check user access to the related room or group.
- Create or revoke guest access.
- Issue user JWT.
- Issue guest JWT.
- Record token issuance metadata.
- Close or cancel meetings.
- Record audit events.

Access inputs:

- User approval state.
- User suspension state.
- User roles.
- Group membership.
- Room membership.
- Meeting type.
- Guest approval state.
- Token expiry.

Portal integration must not expose `JITSI_JWT_APP_SECRET`, token bodies, internal Jitsi hostnames, or component passwords to browsers.

## 13. Reverse Proxy Requirements

Caddy routes Jitsi web traffic to the internal `jitsi-web` service.

Requirements:

- Public HTTPS route for `MEET_DOMAIN`.
- Reverse proxy to `jitsi-web:80`.
- Preserve WebSocket paths required by Jitsi.
- Keep Jitsi internal service ports private.
- Publish only JVB UDP media port where required.
- Do not expose Jitsi internal Prosody, Jicofo, or admin interfaces.
- Keep security headers compatible with Jitsi camera, microphone, and fullscreen use.
- Do not log JWT token bodies or sensitive query strings.

Current public exposure:

| Public Route or Port | Purpose |
| -------------------- | ------- |
| `MEET_DOMAIN` over HTTPS | Jitsi web interface through Caddy. |
| `JITSI_JVB_PORT` UDP | Jitsi media transport. |

The reverse proxy should remain the only public HTTP or HTTPS entrypoint.

## 14. Logging Policy

Jitsi logs should help operators diagnose failures without collecting more meeting metadata than needed.

Log intentionally:

- Service start, stop, restart, and crash events.
- Component connection failures.
- JWT validation failures without token bodies.
- Meeting join failures.
- Jicofo and JVB connectivity problems.
- Media bridge health events.
- Configuration errors.

Do not log:

- `JITSI_JWT_APP_SECRET`.
- Full JWT token bodies.
- Meeting passwords.
- Session cookies.
- Invite tokens.
- Recovery tokens.
- Private participant notes.
- Full request bodies.
- `.env` contents.

Policy:

- Keep debug logging off by default in production.
- Treat meeting names, participant IPs, user agents, and join times as sensitive metadata.
- Keep log retention short unless a deployment has a documented reason.
- Do not commit Jitsi logs to Git.
- Do not paste logs into public support channels without review.

## 15. Backup Requirements

Jitsi backup protects configuration and generated runtime state. Portal backups protect meeting policy and audit records.

Back up:

- `jitsi_web_config` volume.
- `jitsi_prosody_config` volume.
- `jitsi_jicofo_config` volume.
- `jitsi_jvb_config` volume.
- `jitsi/` committed configuration.
- Operator-owned `.env` values through secure storage.
- PostgreSQL portal data for meeting records, guests, token issuance metadata, and audit events.

Do not commit:

- Jitsi generated secrets.
- Jitsi runtime config copied from production.
- `.env`.
- JWT secrets.
- Meeting tokens.
- Logs.
- Recordings, if recordings are ever enabled.

Restore checks:

- Confirm `JITSI_ENABLE_AUTH=1`.
- Confirm `JITSI_ENABLE_GUESTS=0` for MVP.
- Confirm `JWT_ALLOW_EMPTY=0`.
- Confirm `JITSI_JWT_APP_SECRET` is present and not a placeholder.
- Confirm Jitsi web route loads through Caddy.
- Confirm old compromised tokens fail after secret rotation.
- Confirm unauthorized users cannot create public rooms.
- Confirm portal meeting records and audit events are intact.

## 16. Rollback Plan

Jitsi rollback must restore authenticated meeting behavior without changing portal trust records.

Rollback steps:

1. Stop or isolate the public meeting route if Jitsi access is unsafe.
2. Preserve current Jitsi config, logs, and backup manifests for review.
3. Restore the last known-good Jitsi config or volumes.
4. Confirm `JITSI_ENABLE_AUTH=1`.
5. Confirm `JITSI_ENABLE_GUESTS=0`.
6. Confirm `JWT_ALLOW_EMPTY=0`.
7. Rotate `JITSI_JWT_APP_SECRET` if token or secret exposure is suspected.
8. Restart Jitsi services in the required dependency order.
9. Confirm the reverse proxy route for `MEET_DOMAIN`.
10. Issue a test token through the portal for an allowed user.
11. Confirm unauthorized users cannot create or join rooms.
12. Record the rollback result in operator notes or audit events where supported.

Rollback must not delete portal users, roles, groups, invites, verification records, rooms, meetings, audit events, Prosody data, backups, or unrelated service configuration.
