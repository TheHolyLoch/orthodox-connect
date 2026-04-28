# Orthodox Connect Federation Model

## Purpose

Federation allows separate Orthodox Connect servers to communicate in controlled cases without merging their user databases, administrator authority, or local verification records.

The model is trusted federation, not open federation. Each remote server must be reviewed, approved, scoped, monitored, and removable.

## Open Federation Default

Open federation is not allowed by default.

Reasons:

- Parish and group communication depends on local trust and manual verification.
- Public federation creates spam, impersonation, abuse, moderation, and privacy risks.
- External users may not share the same clergy, monastic, parish, or group verification rules.
- Room names, membership, presence, and metadata can reveal sensitive community details.
- Administrators need clear responsibility for external users before messages cross servers.

Federation must remain disabled until a trusted server has been approved and a specific scope has been granted.

## Trusted Server Approval Process

Trusted servers are approved one at a time.

Required approval steps:

1. A local administrator records the request for federation.
2. The requesting server identifies its operator, administrative contact, intended scope, and reason.
3. Local administrators review the trust relationship outside the platform.
4. The proposed scope is limited to the smallest useful room, group, or shared channel set.
5. Both sides agree on abuse handling, revocation timing, logging expectations, and admin contacts.
6. A platform administrator records the approval decision in the audit trail before enabling any configuration.
7. A test period is completed with non-sensitive rooms before sensitive rooms are considered.

Approval must never imply general access to all local rooms or users.

## Server Identity Requirements

Every trusted server must have a stable server identity.

Requirements:

- Public hostname controlled by the trusted operator.
- Valid TLS certificate for the server hostname.
- XMPP domain documented before approval.
- Administrative organization or parish/group name recorded.
- Technical operator name or role recorded.
- Current admin contact details recorded outside public room descriptions.
- Any changed hostname, certificate model, operator, or ownership must trigger re-review.

Placeholder, temporary, or shared test domains must not be approved for production federation.

## Admin Contact Requirements

Each trusted server must provide at least two contact paths where practical.

Required contact details:

- Primary administrative contact.
- Secondary administrative or technical contact.
- Emergency abuse contact.
- Expected response window for urgent reports.
- Out-of-band contact method for verification and incident response.

Contact details should be visible to local administrators, not ordinary users.

## Allowed Federation Scopes

Federation scopes must be explicit.

Allowed scopes:

| Scope                  | Use Case                                           | Default |
| ---------------------- | -------------------------------------------------- | ------- |
| direct_admin_contact   | Admin-to-admin coordination only.                  | Allowed |
| shared_room            | One named room shared between approved servers.    | Allowed |
| shared_group           | A named group with explicit shared room access.    | Allowed |
| clergy_shared_room     | Shared clergy room with extra verification rules.  | Review  |
| monastic_shared_room   | Shared monastic room with extra verification rules.| Review  |
| general_user_presence  | Broad visibility of remote users.                  | Denied  |
| open_domain_messaging  | Any local user can message any remote user.        | Denied  |
| public_room_discovery  | Remote users can browse local rooms.               | Denied  |

Default policy is deny unless a scope is explicitly approved.

## Shared Room and Channel Policy

Shared rooms must be created intentionally and treated as cross-server spaces.

Policy:

- Each shared room must have named local administrators.
- Each shared room must list the approved remote server domains.
- Remote users must be visibly marked as remote where the client supports it.
- Room membership must be explicit and role-based.
- Shared rooms must not expose unrelated local room lists.
- Shared room history retention must be reviewed before adding remote servers.
- Sensitive pastoral, clergy, monastic, or child-related rooms require extra review.
- Removing a trusted server must remove its users from shared rooms.

Shared channels do not create shared administrator authority. Each server remains responsible for its own users.

## Cross-Server Clergy Verification Policy

Clergy verification does not automatically transfer between servers.

Rules:

- A remote clergy label is advisory unless the local server has approved that verification source.
- Local administrators must decide whether remote clergy verification is accepted for each shared scope.
- The approving server, approving administrator, verification date, and scope should be recorded.
- Remote clergy verification must never grant local administrator rights by itself.
- If a remote server revokes clergy status, the local server must be notified through the agreed admin contact path.
- Local administrators may require local confirmation before allowing clergy-only room access.

Monastic and parish administrator verification follow the same conservative model.

## Revocation Process

Federation trust can be revoked by either side.

Revocation triggers:

- Abuse reports are ignored or unresolved.
- Server ownership or operator changes.
- TLS, hostname, or XMPP domain identity changes unexpectedly.
- Public registration or open federation is enabled without notice.
- Verification standards no longer match the approved scope.
- A server is compromised or suspected to be compromised.
- Local administrators decide the relationship is no longer needed.

Revocation steps:

1. Disable federation for the trusted server.
2. Remove remote users from shared rooms and shared groups.
3. Preserve audit records and relevant incident notes.
4. Notify the remote admin contact if safe and appropriate.
5. Review any retained room history exposed during the trust period.
6. Record the revocation reason, actor, timestamp, and affected scopes.

Emergency revocation should favor stopping access first, then completing documentation.

## Abuse Handling

Abuse handling must be agreed before federation is enabled.

Requirements:

- Each server handles its own users first.
- Local administrators may remove or block remote users from local shared rooms immediately.
- Urgent abuse reports must use the agreed emergency contact path.
- Repeat abuse from one server should trigger scope reduction or revocation.
- Reports involving clergy, monastic, parish admin, or minor-related spaces require higher-priority review.
- Abuse reports should include only necessary evidence and avoid unnecessary sensitive content.

No trusted server may require another server to keep a remote user in a local shared room.

## Logging and Audit Requirements

Federation decisions must be auditable.

Audit events should record:

- Trusted server approval request.
- Trusted server approval or rejection.
- Approved federation scopes.
- Admin contacts recorded or changed.
- Shared room creation.
- Remote server added to or removed from a shared room.
- Remote user added to or removed from a shared room.
- Cross-server verification accepted or revoked.
- Abuse report received, escalated, resolved, or closed.
- Federation scope reduced, suspended, or revoked.

Logs should avoid message bodies, invite tokens, recovery tokens, private notes, and unneeded request bodies. Federation logs may contain sensitive metadata and must follow the same retention and backup rules as local audit records.

## Rollback Plan

Rollback must be possible without data loss or broad service downtime.

Rollback steps:

1. Disable federation for the affected remote server.
2. Confirm no new remote sessions can join shared rooms.
3. Remove remote users from local shared room membership lists.
4. Mark affected shared rooms as local-only or suspended.
5. Preserve audit records for the federation period.
6. Notify local room administrators.
7. Notify the remote admin contact if safe and appropriate.
8. Review backups and logs for sensitive exposure.
9. Document whether federation can be restored, reduced, or permanently revoked.

Rollback must not delete local users, local rooms, local audit records, or unrelated trusted server records.
