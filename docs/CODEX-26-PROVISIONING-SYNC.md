# Orthodox Connect Provisioning and Sync Design

## 1. Provisioning Goals

Provisioning should keep Prosody/XMPP and Jitsi aligned with portal identity and access policy without making those services the source of truth.

Goals:

- Keep the portal PostgreSQL database authoritative for accounts, roles, groups, rooms, meetings, suspensions, and audit records.
- Create or enable Prosody accounts only after portal policy allows access.
- Keep public XMPP registration disabled.
- Keep open federation disabled unless a later trusted federation implementation explicitly enables it.
- Map portal room policy into Prosody MUC state without exposing restricted room names or memberships.
- Issue Jitsi meeting tokens only after portal access checks.
- Fail closed when sync state is unclear.
- Make sync idempotent so repeated runs do not widen access.
- Record audit events for provisioning decisions, sync failures, and reconciliation repairs.
- Avoid logging passwords, invite tokens, Jitsi JWT bodies, session cookies, `.env` values, or service secrets.

This document is a design document only. It does not implement sync code, change Prosody configuration, change Jitsi configuration, or change Docker services.

## 2. Source of Truth

The portal database is the source of truth.

Authoritative portal tables include:

| Table                         | Sync Relevance |
| ----------------------------- | -------------- |
| `users`                       | Account state, display name, XMPP JID, suspension, disablement. |
| `groups`                      | Parish, monastery, ministry, shared, and administrative scope. |
| `group_memberships`           | Group access state. |
| `roles`                       | Stable role definitions. |
| `user_roles`                  | Role assignments and revocations. |
| `invites`                     | Invite redemption source records. |
| `verification_requests`       | Requested verified status. |
| `verification_decisions`      | Admin decisions that can assign or revoke verified roles. |
| `rooms`                       | Room policy and target XMPP room JID. |
| `room_memberships`            | Explicit room membership state. |
| `meetings`                    | Jitsi meeting records. |
| `meeting_guests`              | Explicit approved guest access. |
| `meeting_token_issuances`     | Token issuance metadata without token bodies. |
| `audit_events`                | Trust and access decision history. |

Derived systems:

- Prosody stores XMPP runtime state and MUC state.
- Converse.js shows the chat state exposed by Prosody.
- Jitsi validates short-lived JWTs and hosts live meetings.

Prosody and Jitsi state must be treated as derived from portal policy. If service state and portal policy conflict, the reconciliation process should restore the service state to match the portal or disable access until reviewed.

## 3. Portal-to-Prosody Account Provisioning

Prosody account provisioning should happen only after the portal has an approved user state and local policy allows XMPP access.

Target flow:

1. User redeems an invite in the portal.
2. Portal creates a pending user record.
3. Administrator approves the user or assigns the needed access state.
4. Portal derives the user's XMPP JID under `XMPP_DOMAIN`.
5. Portal creates or enables the Prosody account through a reviewed provisioning mechanism.
6. Portal stores the JID in `users.xmpp_jid`.
7. Portal queues or applies room membership sync.
8. Portal writes audit events for the account provisioning action.

Design rules:

- Pending, denied, suspended, and disabled users do not receive active Prosody access.
- Raw XMPP passwords must not be stored in portal audit metadata.
- If Prosody credentials are generated, the initial delivery path must be reviewed separately.
- Account provisioning must be idempotent. Re-running provisioning for an already provisioned approved user should verify state, not create a duplicate account.
- JID generation must prevent collisions and must not let users impersonate clergy, monastic, admin, parish, or official accounts.
- XMPP authentication must not grant portal admin rights.

Possible future mechanisms:

| Mechanism                      | Notes |
| ------------------------------ | ----- |
| Prosody admin command wrapper  | Simple, but needs strict argument handling and secret-safe logging. |
| Prosody module or HTTP API     | Cleaner service boundary, but requires security review. |
| External auth tied to portal   | Strong source-of-truth model, but increases coupling and outage impact. |
| Manual operator provisioning   | Temporary fallback only for small deployments. |

## 4. Portal-to-Prosody Role and Group Mapping

Portal roles and groups should drive XMPP access, but XMPP roles must not become proof of Orthodox Connect verification.

Mapping direction:

| Portal State                         | Prosody Effect |
| ------------------------------------ | -------------- |
| Approved member                      | Eligible for basic XMPP login and member rooms. |
| Active group membership              | Eligible for rooms owned by that group. |
| `clergy_verified`                    | Eligible for clergy-scoped rooms where policy allows. |
| `monastic_verified`                  | Eligible for monastic-scoped rooms where policy allows. |
| `parish_admin`, `diocesan_admin`, `platform_admin` | Eligible for scoped moderation or admin room roles where policy allows. |
| Suspended or disabled user           | XMPP login and room access removed or blocked. |

Rules:

- Portal roles remain authoritative.
- Users must not self-assign privileged status through XMPP nicknames, vCards, profile text, or room roles.
- Prosody MUC affiliation should be derived from portal policy.
- Room moderator or owner status should be granted only when portal policy says the user has that scoped authority.
- Native XMPP clients may not show portal verification labels, so the portal remains the visible verification source.
- Role and group changes should trigger room access recalculation for affected rooms.

## 5. Portal-to-MUC Room Provisioning

Portal room records should drive Prosody MUC room creation and configuration.

Target flow:

1. Authorized administrator creates a room in the portal.
2. Portal records the room scope, owning group, creator, and policy.
3. Portal derives or stores `rooms.xmpp_room_jid` under `XMPP_MUC_DOMAIN`.
4. Sync creates or updates the matching Prosody MUC room.
5. Sync applies privacy, persistence, membership, and moderation settings supported by Prosody.
6. Portal records audit events for room creation and sync result.

Room policy alignment:

| Portal Scope        | MUC Direction |
| ------------------- | ------------- |
| `public_to_members` | Visible and joinable only for approved local members. |
| `group_only`        | Members-only room for active group members. |
| `clergy_only`       | Members-only room for approved clergy where scoped. |
| `monastic_only`     | Members-only room for approved monastics where scoped. |
| `admin_only`        | Members-only room for approved administrator roles. |
| `invite_only`       | Members-only room for explicit room members only. |

Rules:

- Room creation in Prosody must remain restricted.
- Restricted room names should not appear in broad discovery.
- Portal room slugs and MUC JIDs must avoid sensitive real-world details where practical.
- Room configuration sync must be idempotent.
- A failed room sync must not make the room more public.
- Shared inter-group rooms require explicit policy and membership.

## 6. Room Membership Sync

Room membership sync should copy portal-approved room access into Prosody MUC affiliation state.

Access inputs:

- User status.
- User roles.
- Group membership.
- Explicit room membership.
- Room privacy level.
- Suspension or disablement state.
- Meeting or future federation scope where applicable.

Sync rules:

- Approved users with allowed access may receive the needed MUC affiliation.
- Suspended, disabled, removed, or unauthorized users must be removed from the room or set to no affiliation.
- `public_to_members` rooms should include only approved members.
- `group_only` rooms require active membership in the owning group.
- `clergy_only` rooms require approved clergy verification and any local scope check.
- `monastic_only` rooms require approved monastic verification and any local scope check.
- `admin_only` rooms require approved admin role and scope.
- `invite_only` rooms require explicit room membership.
- Room moderator and owner status must be assigned only through portal authority.

Membership changes should create audit events when the portal decision changes. Routine idempotent sync confirmations may be logged operationally without creating excessive audit noise unless a deployment policy requires full sync audit records.

## 7. Invite Redemption Sync

Invite redemption creates portal state first. It should not immediately create broad XMPP access.

Target flow:

1. User redeems a valid invite.
2. Portal creates a pending user.
3. Portal records invite redemption and group scope where applicable.
4. Portal records an audit event.
5. User waits for approval if local policy requires review.
6. Prosody account provisioning happens only after approval.

Rules:

- Expired, revoked, and already-used single-use invites must not create Prosody accounts.
- Reusable invites remain explicit and audited.
- Invite redemption may create pending group membership, but pending membership does not grant active room access.
- Users must not receive clergy, monastic, parish admin, diocesan admin, or platform admin status through invite redemption alone.
- Sync failures during invite redemption should not expose chat or meeting access.

## 8. Verification Role Sync

Verification decisions can change chat and meeting access, so they must trigger derived sync work.

Supported verification types:

- `clergy`
- `monastic`
- `parish_admin`

Target behavior:

- Approved clergy verification assigns `clergy_verified`.
- Approved monastic verification assigns `monastic_verified`.
- Approved parish admin verification assigns `parish_admin`.
- Rejected requests do not assign privileged roles.
- Revoked verification removes or disables the derived role assignment.

Sync effects:

- Recalculate access for clergy-only, monastic-only, admin-only, and group-scoped rooms.
- Apply or remove Prosody MUC affiliations.
- Allow or deny Jitsi meeting creation based on creator role policy.
- Keep room membership and meeting token issuance aligned with current role state.

Rules:

- Every verification decision must be tied to an admin user.
- Every verification decision must create an audit event.
- Users must not approve their own privileged status.
- XMPP room roles or display names must not substitute for portal verification.
- Role revocation should remove derived room access unless another valid policy still allows access.

## 9. Account Suspension Sync

Suspension must quickly remove active access across portal, Prosody, rooms, and meetings.

Suspension effects:

- Portal sessions should be invalidated where supported.
- Prosody account login should be disabled or credentials invalidated.
- Existing room memberships should be removed, suspended, or made inactive in derived Prosody state.
- New Jitsi token issuance must stop.
- Existing short-lived Jitsi JWTs should be allowed to expire quickly unless secret rotation is required.
- Guest records created by the suspended account should be reviewed where applicable.

Rules:

- Suspension must fail closed.
- A suspended user must not be able to reconnect to chat through Converse.js or native XMPP clients.
- A suspended user must not receive new room memberships.
- A suspended user must not create or join meetings.
- Suspension and restoration must create audit events.
- Restoration should re-run reconciliation before access is considered healthy.

If a compromise is suspected, operators may need to rotate portal sessions, Prosody credentials, Jitsi JWT secrets, or other secrets depending on exposure.

## 10. Account Deletion and Deactivation Sync

Deactivation is preferred over hard deletion because trust records, audit history, backups, and room history may need to remain reviewable.

Deactivation behavior:

- Set portal user status to `disabled` or equivalent.
- Disable Prosody login.
- Remove active MUC affiliations.
- Stop Jitsi token issuance.
- Preserve audit events.
- Preserve enough identifiers to prevent impersonation through account reuse.

Hard deletion considerations:

- Hard deletion should be a separate reviewed workflow.
- Deletion affects portal records, Prosody account data, room memberships, meetings, audit references, backups, and future exports.
- Audit records should not be deleted as the normal way to reverse a decision.
- Backups may retain deleted data until retention removes them.

Rules:

- Deleted or disabled users must not retain active verified labels.
- Deleted or disabled users must not retain active room access.
- Deleted or disabled users must not create or join Jitsi meetings.
- Recreating a deleted account with the same display name or JID must require administrator review.

## 11. Jitsi Meeting Token Provisioning

Jitsi does not need long-lived account sync for ordinary meeting access. The portal should issue short-lived JWTs after policy checks.

Token issuance flow:

1. User or approved guest requests a meeting link.
2. Portal checks meeting status, user status, roles, group membership, room access, guest approval, and token expiry policy.
3. Portal creates a short-lived JWT using `JITSI_JWT_APP_ID` and `JITSI_JWT_APP_SECRET`.
4. Portal returns the meeting link to the requester.
5. Portal records token issuance metadata without storing the token body.
6. Portal records an audit event.

Rules:

- Meeting creation remains role-gated.
- Anonymous public room creation remains disabled.
- Meeting names alone must not grant access.
- Guests can join only through explicit approved guest records.
- Suspended or disabled users must not receive tokens.
- Token bodies must not be stored in `meeting_token_issuances`, logs, audit metadata, screenshots, or support output.
- Tokens should be short-lived enough that suspension and policy changes take effect quickly.
- Secret rotation invalidates old tokens and should be recorded by operators.

## 12. Failure Handling

Provisioning failures must fail closed and be visible to administrators.

Failure handling rules:

- If account provisioning fails, the user should not receive chat access.
- If room creation fails, the room should not become public or discoverable by mistake.
- If membership sync fails, access should not be widened.
- If Jitsi token policy cannot be checked, token issuance should be denied.
- If Prosody state cannot be inspected, reconciliation should mark affected sync work as failed and require review.
- Failed sync attempts should be retried with backoff where practical.
- Sync logs must not include passwords, raw invite tokens, JWT bodies, session cookies, `.env` values, or database URLs with passwords.

The portal should eventually track sync state for users, rooms, memberships, and meetings so admins can distinguish pending sync, successful sync, failed sync, and manually paused sync.

## 13. Reconciliation Job Design

A reconciliation job should compare portal desired state with derived service state and repair drift.

Design requirements:

- Run manually first, then on a schedule only after operators trust the behavior.
- Support a dry-run mode that reports planned changes without applying them.
- Support an apply mode that makes idempotent changes.
- Use a lock so two reconciliation runs do not modify the same service state at once.
- Process users, roles, groups, rooms, room memberships, suspensions, disabled accounts, meetings, guest expiries, and token policy state.
- Prefer small batches and clear failure records over one large opaque run.
- Never enable public registration or open federation.
- Never create real users outside portal records.
- Never print secrets.

Suggested reconciliation checks:

| Check                       | Desired Result |
| --------------------------- | -------------- |
| Approved user has JID       | Prosody account exists and is enabled. |
| Pending user has no access  | Prosody account absent or disabled. |
| Suspended user blocked      | Prosody login disabled and MUC access removed. |
| Room exists in portal       | Matching MUC room exists with restricted creation and policy. |
| Room membership active      | Matching MUC affiliation exists if access is allowed. |
| Role revoked                | Derived room access removed unless another policy allows it. |
| Meeting closed              | No new Jitsi tokens issued. |
| Guest expired               | No new guest token issued. |

Reconciliation should record summary results in operational logs and important access repairs in audit events.

## 14. Audit Requirements

Provisioning must leave a reviewable record without storing secrets.

Audit events should cover:

- Prosody account provisioned.
- Prosody account disabled.
- Prosody account provisioning failed.
- XMPP JID assigned.
- Room provisioning queued, applied, or failed.
- Room membership synced or removed because policy changed.
- Role-derived access applied or removed.
- Suspension sync applied.
- Deactivation sync applied.
- Jitsi meeting token issued.
- Guest meeting token issued.
- Reconciliation started and completed.
- Reconciliation repaired access drift.
- Reconciliation failed and requires admin review.

Audit metadata may include:

- Actor user ID.
- Target user ID.
- Entity type and ID.
- Room ID.
- Meeting ID.
- Scope group ID.
- Safe status values.
- Failure category.
- Request or job ID.

Audit metadata must not include:

- Passwords.
- Raw invite tokens.
- Raw recovery tokens.
- Jitsi JWT bodies.
- Session cookies.
- Full database URLs with passwords.
- `.env` contents.
- Message bodies.
- Private pastoral notes.

## 15. Rollback Plan

Provisioning rollback should remove unsafe sync behavior without deleting authoritative portal records.

Rollback steps:

1. Disable the sync worker or manual sync command.
2. Stop affected public routes if current derived service state is unsafe.
3. Preserve portal database state, Prosody data, Jitsi config, logs, and backup manifests for review.
4. Restore the last known-good Prosody or Jitsi service state only if needed.
5. Confirm public XMPP registration remains disabled.
6. Confirm open federation remains disabled.
7. Confirm Jitsi authentication remains enabled.
8. Confirm suspended and disabled users cannot receive new access.
9. Run reconciliation in dry-run mode after restoring the previous state.
10. Apply only reviewed repairs.
11. Rotate exposed secrets if provisioning logs or failures leaked credentials or tokens.
12. Record rollback and repair actions in audit events or operator notes.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, backups, Prosody data, Jitsi state, or unrelated service configuration.
