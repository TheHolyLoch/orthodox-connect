# Orthodox Connect Privacy and Data Policy

## Privacy Goals

Orthodox Connect should collect only the data needed to operate a private, invite-only, manually verified community.

Goals:

- Keep user data limited and purposeful.
- Keep public registration disabled.
- Keep clergy, monastic, and parish administrator status controlled by manual verification.
- Keep private notes and verification details visible only to authorized administrators.
- Keep audit records for trust and access decisions without turning logs into a second profile database.
- Avoid storing message content in portal records unless a later reviewed feature requires it.
- Keep backups, logs, exports, and restore targets protected like sensitive community records.
- Avoid legal claims in product documentation.

This document is a design policy. It does not implement privacy controls or replace local legal review.

## Data Minimisation Rules

Data collection should follow least-need rules.

Rules:

- Collect only data needed for account access, invitation, verification, roles, rooms, meetings, audit, backup, and recovery.
- Avoid government identity documents by default.
- Avoid birth dates by default.
- Avoid home addresses by default.
- Avoid broad profile fields by default.
- Avoid private pastoral notes.
- Avoid storing message bodies in portal audit or moderation records by default.
- Avoid logging invite tokens, recovery tokens, passwords, session cookies, JWT bodies, and `.env` contents.
- Keep debug logging off by default in production.
- Use fake data in local development and staging.
- Keep production data out of lower environments unless scrubbed and approved.

If a workflow can work with a stable user ID instead of personal details, prefer the stable user ID.

## User Data Collected

User data should support account identity, access control, and administrator review.

Expected user data:

| Data Type          | Purpose |
| ------------------ | ------- |
| Account ID         | Stable internal identifier. |
| Username or login  | Account sign-in and display where needed. |
| Display name       | Human-readable account label. |
| Password hash      | Authentication when portal login is implemented. |
| Account state      | Pending, approved, denied, suspended, disabled, or similar state. |
| Group membership   | Parish, monastery, mission, ministry, or other approved group access. |
| Role assignments   | Member, clergy, monastic, parish admin, diocesan admin, platform admin, or related roles. |
| Room memberships   | Explicit access to rooms where policy requires it. |
| Meeting records    | Meeting creation and token issuance metadata. |
| Timestamps         | Creation, update, approval, suspension, and access decision times. |

User-facing profile data should stay minimal. Users must not be able to self-assign verified clergy, monastic, parish admin, diocesan admin, or platform admin labels.

## Admin-Only Data

Some data should be visible only to authorized administrators.

Admin-only data:

- Internal verification notes.
- Rejection reasons for verification requests.
- Invite creator and invite status details.
- Suspension reasons.
- Recovery review notes when recovery is implemented.
- Admin audit views.
- Abuse reports and report evidence when moderation is implemented.
- Source metadata such as IP address or user agent where policy allows it.
- Emergency operator notes stored outside the repository.

Admin-only data should be scoped. A parish administrator should not automatically see data for every parish, group, monastery, or future trusted server unless their role grants that scope.

## Verification Data

Verification data is sensitive because it records trust decisions.

Supported verification types:

- `clergy`
- `monastic`
- `parish_admin`

Verification records should include:

- Requesting user.
- Requested verification type.
- Request status.
- Deciding administrator.
- Decision timestamp.
- Approval or rejection state.
- Rejection reason where applicable.
- Minimal note needed to support the decision.

Verification records should not become pastoral files, personnel files, or broad biographical records. Clergy and monastic labels must appear only after administrator approval.

Revoked or suspended verification status should remain auditable. Deleting verification history should not be the normal way to reverse a decision.

## Audit Log Data

Audit logs are records of trust and access decisions.

Audit logs should record:

- Actor user ID.
- Target user or resource ID.
- Resource type.
- Event type.
- Scope.
- Timestamp.
- Reason or short note where needed.
- Request ID or route metadata where available.
- Minimal source metadata if deployment policy allows it.

Audit events should cover:

- Invite creation, revocation, and redemption.
- Verification request creation, approval, and rejection.
- Role assignment and removal.
- Group membership changes.
- Room creation, policy changes, and membership changes.
- Meeting creation and token issuance.
- Suspension and restoration.
- Backup and restore events where supported.
- Federation, library, Tor, IRC, and moderation actions if those features are implemented later.

Audit logs must not store passwords, session cookies, invite tokens, recovery tokens, JWT bodies, full request bodies, private message content, or long private notes.

## Chat Data Policy

Prosody is the chat service. Chat data policy depends on Prosody configuration, selected modules, client behavior, and room settings.

Chat data may include:

- XMPP account identifiers.
- Room names.
- Room membership.
- Presence and join metadata.
- Message metadata.
- Message history if archiving is enabled.
- Client connection metadata in service logs.

Policy:

- Public registration remains disabled.
- Open federation remains disabled by default.
- Room access remains role and membership based.
- Restricted room names and membership should not be exposed to users without access.
- Message bodies should not be copied into portal audit records by default.
- Message archive settings must be reviewed before production use.
- Do not claim platform-wide end-to-end encryption unless the selected clients and workflow provide it for that feature.
- External XMPP clients may not show portal verification labels consistently.

Chat logs and Prosody backups can reveal sensitive community metadata and must be protected.

## Jitsi Meeting Data Policy

Jitsi meeting access is tied to portal policy and JWT authentication.

Jitsi data may include:

- Meeting names.
- Meeting creator metadata.
- Meeting join metadata.
- Guest access metadata.
- JWT validation failures.
- Component logs.
- Participant IP addresses or client metadata in service logs.

Policy:

- Public anonymous meeting creation remains disabled.
- Meeting creation remains role-gated.
- Meeting names alone must not grant access.
- Jitsi JWT secrets and token bodies must not be logged.
- Guest access must be explicit and auditable.
- Recordings should be disabled by default.
- If recordings are added later, storage, consent, access control, retention, and deletion policy must be reviewed first.

Jitsi service logs and configuration backups are sensitive and should be protected like other service data.

## Library Data Policy Placeholder

The library service is later scope. No library service is currently deployed.

Future library data may include:

- Library user accounts or mappings.
- Collection access rules.
- Book or PDF metadata.
- Uploaded files.
- Import records.
- Search indexes.
- Reading progress or reading history if enabled.

Future policy:

- No anonymous public library access by default.
- Library access should be tied to portal roles or explicit collection policy.
- Copyright and permission status should be recorded before publication.
- Search must not reveal restricted collections.
- Reading history should be optional and reviewed before enabling.
- Library files and metadata must not be committed to Git.
- Library backups may be large and sensitive.

Library privacy must be reviewed again before a service is added.

## Data Retention Policy

Retention should be short unless operational, audit, or recovery needs require longer retention.

Suggested retention model:

| Data Type              | Retention Direction |
| ---------------------- | ------------------- |
| Active user records    | Keep while account is active. |
| Suspended user records | Keep while suspension, appeal, or safety review requires it. |
| Invite records         | Keep long enough to audit invite creation, revocation, and redemption. |
| Verification records   | Keep while verified status, revocation history, or audit review requires it. |
| Audit events           | Policy-defined and treated as trust records. |
| Container logs         | Short retention, often 7 to 14 days. |
| Security event logs    | Short to moderate retention, often 30 to 90 days. |
| Backups                | Keep per operator backup schedule and delete old backups deliberately. |
| Debug logs             | Disabled by default and deleted after troubleshooting. |

Retention should be reviewed before enabling federation, Tor access, library service, IRC bridge, moderation evidence storage, or message archiving.

## Data Export Policy

Export should be controlled and scoped.

Allowed export types:

- User's own account data where implemented.
- Administrator export of users, roles, groups, invites, verification records, rooms, meetings, and audit records for the administrator's scope.
- Backup exports for disaster recovery.
- Future migration exports after a versioned migration design exists.

Export rules:

- Exports must require authorization.
- Exports should include only the requested scope.
- Exports must not include passwords, session cookies, invite tokens, recovery tokens, JWT bodies, `.env`, TLS private keys, onion keys, or backup encryption keys.
- Exports containing real data must not be committed to Git.
- Exports should be stored only in operator-approved locations.
- Export and migration formats should be documented before external API or migration tooling is implemented.

Federated, library, and IRC export behavior must be reviewed separately before those features exist.

## Data Deletion Policy

Deletion must preserve safety, auditability, and recovery needs.

Deletion rules:

- Suspension and disablement are preferred over hard deletion for active trust and safety cases.
- Audit records should not be deleted as the normal way to reverse a decision.
- Corrections should create new audit events.
- Deleted or disabled users should lose portal, chat, room, and meeting access.
- Deleted or disabled users should not retain active verified labels.
- Invite tokens, recovery tokens, and sessions should be revoked when an account is disabled or deleted.
- Backups may retain deleted data until backup retention removes them.

Hard deletion needs a separate implementation plan because it affects users, roles, verification records, audit events, Prosody data, Jitsi records, backups, and future exports.

## Admin Access Rules

Administrator access must be role-scoped and auditable.

Rules:

- Admin actions require approved admin roles.
- `parish_admin` access should be scoped to assigned parish or group boundaries.
- `diocesan_admin` access should be scoped to assigned diocesan boundaries.
- `platform_admin` access should be rare and limited to trusted operators.
- Admins must not share accounts.
- Admin sessions should expire sooner than normal sessions when implemented.
- Admin recovery should require stronger review.
- Admin access to verification notes, abuse reports, exports, and backups should be limited to those with a need to review them.
- Admin access changes should create audit events.

Operators should review privileged access on a regular schedule.

## Breach Response Outline

A breach response should protect users, preserve evidence, and restore trust.

Response outline:

1. Contain the affected service, route, account, token, or host.
2. Preserve relevant logs, audit events, backup manifests, and operator notes.
3. Identify exposed data types and affected scopes.
4. Rotate exposed secrets, tokens, passwords, JWT secrets, TLS keys, or backup keys as needed.
5. Suspend compromised accounts where needed.
6. Revoke affected invites, sessions, recovery tokens, and meeting tokens.
7. Restore from a known-good backup only if data integrity is unsafe.
8. Review whether Prosody, Jitsi, Caddy, PostgreSQL, portal, backups, or `.env` were affected.
9. Notify affected administrators and users through an approved local communication path.
10. Record follow-up actions and policy changes.

This outline does not make legal claims or replace local incident-response obligations.

## Rollback Plan

Privacy policy rollback should restore the previous privacy guidance without changing application behavior.

Rollback steps:

1. Revert the faulty privacy guidance.
2. Confirm no application code or Docker services were changed by the policy edit.
3. Confirm no real user data was added to the repository.
4. Confirm no legal claims were added.
5. Confirm public registration remains disabled.
6. Confirm federation remains disabled.
7. Confirm admin-only notes remain admin-only in current workflows.
8. Confirm logs, backups, and exports remain excluded from Git.
9. Preserve audit events and incident notes.
10. Record what guidance was reverted and why.

Rollback must not delete users, roles, groups, invites, verification records, rooms, meetings, audit events, backups, Prosody data, Jitsi state, or unrelated service configuration.
