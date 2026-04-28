# Orthodox Connect Portal Design

## 1. Portal Goals

The portal is the control plane for Orthodox Connect trust, access, and administrator workflows.

Goals:

- Keep registration invite-only.
- Let approved users see account status, allowed rooms, and allowed meetings.
- Let users request verification for supported trust roles.
- Let administrators manage invites, users, groups, roles, verification requests, rooms, meetings, and audit records.
- Keep clergy, monastic, parish admin, diocesan admin, and platform admin status administrator-controlled.
- Keep room and meeting access derived from portal data.
- Record trust and access decisions in audit events.
- Avoid exposing private notes, raw tokens, session cookies, passwords, JWT bodies, internal hostnames, or service secrets.
- Keep ordinary user workflows simple enough for non-technical parish, diocesan, monastic, and community users.

The portal must not become a public social network, parish management system, pastoral file system, or replacement for local administrator judgment.

## 2. Portal Role in the Platform

The portal owns account and access policy. PostgreSQL stores portal state.

Portal responsibilities:

- Invite creation, listing, revocation, and redemption.
- User status tracking.
- Manual verification requests and decisions.
- Role and group membership management.
- Room and channel policy.
- Jitsi meeting creation, guest approval, and token issuance.
- Audit event recording and review.
- Minimal user-facing account and access pages.
- Minimal admin-facing workflow pages.

Other service responsibilities:

| Service          | Responsibility |
| ---------------- | -------------- |
| PostgreSQL       | Stores portal identity, policy, meeting, and audit records. |
| Prosody          | Handles XMPP login, direct messages, and group chat after accounts exist. |
| Converse.js      | Provides browser chat access to Prosody. |
| Jitsi Meet       | Provides authenticated video meetings using portal-issued access. |
| Caddy            | Routes public HTTPS traffic to portal, chat, XMPP browser transports, and meetings. |

Current limits:

- Portal production packaging is not done.
- Prosody account provisioning is not automated yet.
- Email delivery for invite and recovery flows is not implemented.
- Account recovery and full login hardening remain future work.

## 3. User-Facing Pages

User-facing pages should be small, clear, and limited to implemented workflows.

Planned pages:

| Page                   | Purpose |
| ---------------------- | ------- |
| Invite redemption      | Accept a valid invite and create a pending account. |
| Sign in                | Authenticate an existing portal user when portal login is implemented. |
| Account status         | Show pending, approved, denied, suspended, or disabled state. |
| Verification requests  | Submit and view the user's own verification requests. |
| Rooms                  | Show rooms the user may access once room listing is user-facing. |
| Meetings               | Show meetings and links the user may access. |
| Help or contact        | Show local administrator contact guidance without exposing private data. |

User-facing rules:

- Do not show admin-only notes.
- Do not show raw invite tokens after redemption.
- Do not expose private room names to users without access.
- Do not expose JWTs or token contents.
- Do not let users assign roles, group membership, room membership, or verified status to themselves.
- Suspended users should see a limited status page and no active room or meeting navigation.

## 4. Admin-Facing Pages

Admin pages should prioritize review, decisions, and auditability over broad dashboards.

Admin pages:

| Page                    | Purpose |
| ----------------------- | ------- |
| Admin overview          | Show pending work and links to admin sections. |
| Users                   | View users by status and inspect account state. |
| Groups and parishes     | View and manage local groups, parishes, monasteries, ministries, and shared groups. |
| Roles                   | View roles and assigned users where permitted. |
| Invites                 | Create, list, and revoke invites. |
| Verification requests   | Review pending, approved, and denied requests. |
| Rooms and channels      | Create rooms, set room scope, and manage membership. |
| Meetings                | Create meetings, approve guests, and issue access links or tokens. |
| Audit events            | Review trust and access decisions. |

Admin-facing rules:

- Admin pages require approved admin roles.
- Admin authority must be scoped by role and group where applicable.
- Privileged actions require clear forms and confirmation where risk is high.
- Lists should support filtering by status, group, role, request type, and date where practical.
- Admin pages must not expose secrets or full token bodies.

## 5. Authentication Flow

Portal authentication should use server-managed sessions for browser use.

Preferred flow:

1. User opens the portal hostname.
2. User enters portal credentials.
3. Portal validates credentials against PostgreSQL-backed account data.
4. Portal checks account status.
5. Portal creates a secure server-managed session.
6. Portal derives permissions from roles, groups, suspension state, and scope.
7. Portal redirects the user to account status, user pages, or admin pages based on permissions.

Rules:

- Public registration remains unavailable.
- Invite redemption remains the only normal account creation path.
- Suspended and disabled users cannot access private workflows.
- Admin sessions should expire sooner than ordinary user sessions when implemented.
- Session cookies must be HTTP-only, secure in production, and excluded from logs.
- Authentication failures should be logged as security metadata without storing passwords.
- Password reset and recovery are future workflows and must not bypass suspension or verification.

## 6. Invite Redemption Flow

Invite redemption creates a limited pending account.

Flow:

1. Administrator creates an invite with expiry, creator, scope, and reusable flag.
2. Invite token is delivered through an approved out-of-band path.
3. User opens the invite redemption page.
4. Portal checks token hash, status, expiry, and single-use or reusable behavior.
5. Portal collects only required account fields.
6. Portal creates a pending user.
7. Portal applies pending group membership when the invite has a group scope.
8. Portal updates invite status or use count.
9. Portal records an audit event.
10. User sees a clear pending approval or next-step page.

Rejection cases:

- Expired invite.
- Revoked invite.
- Already-used single-use invite.
- Unknown token.
- Invalid account data.

Invite pages must not reveal token hashes, raw database errors, or whether unrelated accounts exist.

## 7. Verification Request Flow

Verification requests let users ask for specific trusted status. They do not grant status by themselves.

Supported request types:

- `clergy`
- `monastic`
- `parish_admin`

User flow:

1. Approved or pending user opens verification request page where policy allows it.
2. User selects one supported verification type.
3. User adds a short note if local policy asks for it.
4. Portal creates a pending verification request.
5. Portal records an audit event.
6. User sees request status.

Rules:

- Users cannot approve their own requests.
- Users cannot request unsupported role types through this workflow.
- Request notes should be short and operational.
- Verification request pages must not imply automatic approval.
- Suspended or disabled users should not create new verification requests.

## 8. Verification Review Flow

Verification review is an administrator workflow.

Review flow:

1. Authorized admin opens pending verification requests.
2. Admin reviews request type, user state, group scope, and minimal notes.
3. Admin approves or rejects the request.
4. Approved requests assign the matching role.
5. Rejected requests require a reason.
6. Portal stores the verification decision tied to the admin user.
7. Portal records an audit event.
8. User status pages show the new request state and visible verified label where appropriate.

Rules:

- Every decision must be tied to an admin user.
- Admins must not approve their own privileged status.
- `clergy_verified`, `monastic_verified`, and `parish_admin` must only come from approved decisions or explicit admin role assignment.
- Internal verification notes and rejection reasons are visible only to authorized admins unless local policy exposes a user-safe message.
- Revocation or correction should create new audit events rather than deleting history.

## 9. Group and Parish Management

Groups model parishes, monasteries, missions, ministries, shared groups, and administrative scopes.

Group types:

- `parish`
- `monastery`
- `mission`
- `ministry`
- `shared`
- `administrative`

Admin capabilities:

- Create and update groups where authorized.
- View group membership.
- Add or remove users from groups.
- Set membership status.
- Scope roles and rooms to groups.
- Review group-related audit events.

Rules:

- Group membership must be explicit.
- Group-scoped admins act only within their approved scope.
- Shared groups must not imply access to all rooms in participating groups.
- Sensitive group names and membership lists should be visible only to authorized users.
- Group changes should create audit events when they affect access.

## 10. Room and Channel Management

Rooms and channels are portal-controlled access records that should align with Prosody MUC rooms.

Supported room scopes:

- `public_to_members`
- `group_only`
- `clergy_only`
- `monastic_only`
- `admin_only`
- `invite_only`

Admin capabilities:

- Create rooms.
- Assign room group scope.
- Set room privacy level.
- Add and remove room members.
- Change room membership status.
- Check whether a user may access a room.
- View room-related audit events.

Rules:

- Room access is derived from account status, group membership, roles, explicit membership, and suspension state.
- Room membership records are created only when access rules allow it.
- Suspended users cannot access rooms.
- Private, clergy, monastic, admin, youth, and pastoral room names should not be exposed to unauthorized users.
- Prosody synchronization remains separate until implemented.
- Room creation and membership changes must create audit events.

## 11. Jitsi Meeting Management

The portal controls official Jitsi meeting access.

Meeting capabilities:

- Create meetings for allowed roles.
- Tie a meeting to a portal room where appropriate.
- List meetings visible to allowed users and administrators.
- Approve explicit guests where local policy allows.
- Issue user meeting tokens.
- Issue guest meeting tokens.
- Close or cancel meetings.
- View meeting-related audit events.

Rules:

- Anonymous public room creation remains disabled.
- Meeting creation is role-gated.
- Meeting names and slugs must not grant access by themselves.
- Jitsi JWTs are issued only after portal checks.
- Token bodies must not be stored or logged.
- Guest access must be explicit, expiring, and revocable.
- Meeting creation and token issuance must create audit events.

Allowed meeting creator roles come from `JITSI_MEETING_CREATOR_ROLES` and currently include administrator roles and `clergy_verified` where local policy allows it.

## 12. Audit Log Views

Audit views show trust and access decisions to authorized administrators.

Audit views should support:

- Newest-first event listing.
- Filter by actor.
- Filter by target user.
- Filter by entity type.
- Filter by action.
- Filter by group scope.
- Filter by time range.
- Detail view for a single audit event.

Audit event examples:

- Invite created, revoked, and redeemed.
- Verification requested, approved, and rejected.
- Role assigned and revoked.
- Group membership changed.
- Room created, access changed, and membership changed.
- Meeting created and token issued.
- Account suspended or restored when implemented.

Rules:

- Audit events are append-only from the application perspective.
- Audit views require admin roles.
- Audit metadata must not contain passwords, raw tokens, JWT bodies, session cookies, message bodies, or private pastoral notes.
- Corrections should create new audit events.

## 13. Permission Checks

Permission checks must happen server-side for every portal route and action.

Required checks:

- User is authenticated for private pages.
- User is not suspended or disabled.
- Admin routes require approved admin roles.
- Group-scoped actions require authority over the group.
- Verification approval requires an authorized admin and cannot be self-approved.
- Role assignment cannot be self-granted by ordinary users.
- Room access must use portal access policy.
- Meeting creation must use creator role policy.
- Meeting token issuance must check user or guest access.
- Audit views require authorized admin access.

UI visibility is not authorization. Hidden buttons, links, or form fields must not be treated as the permission boundary.

## 14. Error Handling

Portal errors should be clear to users and safe for logs.

User-facing behavior:

- Expired invite: say the invite expired and to ask an administrator for a new one.
- Revoked invite: say the invite is no longer valid.
- Already-used invite: say the invite was already used.
- Pending account: say the account is waiting for administrator review.
- Suspended account: say the account cannot access the service and to contact an administrator.
- Missing room access: say the room is not available to this account.
- Meeting denied: say the meeting is not available to this account or link.
- Unauthorized admin action: say the user does not have permission.

Rules:

- Do not expose stack traces.
- Do not expose SQL errors.
- Do not expose internal hostnames.
- Do not expose raw tokens, token hashes, JWT contents, session cookies, or secrets.
- Log stable IDs and event types where useful, not full sensitive payloads.
- Authorization-sensitive lookups may return not found when revealing existence would expose private data.

## 15. Accessibility Requirements

The portal should be usable by ordinary parish users and administrators on desktop and mobile browsers.

Requirements:

- Use readable font sizes.
- Keep strong contrast for text and controls.
- Do not rely on color alone for status.
- Label all form fields.
- Keep focus order logical.
- Make buttons and links distinct.
- Keep confirmation screens keyboard accessible.
- Keep admin tables readable and provide mobile-friendly layouts where practical.
- Put error messages near the relevant field.
- Use plain text status labels with accessible names.
- Avoid icon-only actions unless they have accessible names.
- Keep invite redemption, account status, verification requests, and meeting links usable on narrow screens.

Accessibility should be verified before broad parish use, especially for invite redemption and admin review workflows.

## 16. Rollback Plan

Portal rollback must preserve trust records and avoid opening access too broadly.

Rollback steps:

1. Stop affected portal routes or actions if the current behavior is unsafe.
2. Preserve PostgreSQL state, logs, and backup manifests for review.
3. Restore the last known-good portal code or template.
4. Confirm public registration remains unavailable.
5. Confirm admin routes require approved admin roles.
6. Confirm suspended users remain blocked.
7. Confirm invite redemption rejects expired, revoked, and already-used single-use invites.
8. Confirm verification decisions require authorized admins.
9. Confirm room access denies unauthorized users.
10. Confirm Jitsi meeting creation and token issuance remain role-gated.
11. Preserve audit events created before rollback.
12. Add corrective audit events for any manual data repair.
13. Rotate secrets if sessions, passwords, JWTs, invite tokens, or recovery tokens were exposed.
14. Restore from backup only if data integrity cannot be repaired safely.

Rollback must not delete users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
