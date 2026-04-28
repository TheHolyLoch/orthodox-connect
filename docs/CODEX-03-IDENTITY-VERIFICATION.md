# Orthodox Connect Identity and Verification

## Purpose

The identity system exists to keep Orthodox Connect invite-only, manually verified, and role-aware. It should support parish and group membership, clergy verification, monastic verification, visible verified status, room access policy, audit trails, suspension, and recovery.

The system must not allow public self-asserted clergy or monastic labels. Clergy and monastic status must be granted only through an administrator-controlled verification workflow.

## Core Rules

- Registration is invite-only.
- New accounts require manual approval before normal access.
- Parish and group membership must be explicit.
- Clergy verification must be granted by authorized administrators.
- Monastic verification must be granted by authorized administrators.
- Room access must come from role, parish, group, or explicit membership policy.
- Verified status may be visible to users where it helps trust and moderation.
- Verification decisions must create audit records.
- Suspended accounts must lose access to chat, rooms, meetings, and recovery actions until restored.
- Account recovery must not bypass verification or suspension.
- Users must not be able to apply public clergy or monastic labels to themselves.

## Current Implementation

The portal stores identity and access state in PostgreSQL migrations under `portal/migrations/`.

Implemented portal workflows:

- Invite creation, listing, redemption, revocation, expiry, and reusable invite flags.
- Pending users created through invite redemption.
- Verification requests for `clergy`, `monastic`, and `parish_admin`.
- Admin approval and rejection of verification requests.
- Role assignment from approved verification decisions.
- Room definitions and room membership checks.
- Meeting creation and token issuance tied to approved users or approved guests.
- Audit events for invite, verification, room, and meeting actions.

Current limits:

- No public registration endpoint exists.
- No full user self-service account UI exists.
- Prosody account creation is not automated yet.
- Email delivery for invites is not implemented.

## Roles

| Role               | Purpose                                                                    |
| ------------------ | -------------------------------------------------------------------------- |
| guest              | Limited invited user with minimal access before approval or membership.     |
| inquirer           | Approved user exploring parish life or catechism with limited access.       |
| member             | Verified parish or group member with normal community access.               |
| parish_admin       | Local administrator for invitations, membership, verification, and rooms.    |
| clergy_verified    | Verified clergy status granted through manual review.                       |
| monastic_verified  | Verified monastic status granted through manual review.                     |
| diocesan_admin     | Higher-scope administrator for diocesan or multi-parish oversight.          |
| platform_admin     | Instance-level administrator with technical and emergency authority.         |

Roles are additive. A user may be both `member` and `clergy_verified`, or both `parish_admin` and `clergy_verified`.

## Invite-Only Registration

Invitation flow:

1. An authorized administrator creates an invitation.
2. The invitation is scoped to a parish, group, role expectation, or limited guest access.
3. The invitation is delivered through an approved out-of-band method.
4. The invited person opens the invite and creates account credentials.
5. The account starts as `guest` or another limited pending state.
6. The account cannot self-grant verified, clergy, monastic, or administrative roles.
7. The invitation record is marked accepted, expired, revoked, or unused.

Invitation requirements:

- Invitations should expire.
- Invitations should be revocable.
- Invitations should be single-use unless an administrator explicitly creates a reusable invite for a limited use case.
- Invitation records should show creator, scope, status, and timestamps.
- Invitation links must not be committed to Git or logged in public places.

## Manual Approval

Manual approval turns a limited account into an approved participant.

Approval states:

- pending
- approved
- denied
- suspended
- disabled

An administrator should review the user before approval. The review method can depend on the parish or group policy, such as known parish membership, direct contact, clergy confirmation, or another local verification method.

Approval must record:

- Reviewed user.
- Reviewing administrator.
- Decision.
- Scope of approval.
- Timestamp.
- Short reason or note where needed.

## Parish and Group Membership

Parish and group membership define where a user belongs.

Membership types:

- parish membership
- monastery community membership
- mission or chapel membership
- ministry group membership
- shared inter-group channel membership
- guest access to a specific group or room

Membership states:

- invited
- pending
- active
- suspended
- removed

Membership should be managed in the portal and enforced in Prosody room access. A user can belong to more than one parish or group only if the deployment policy allows it.

## Clergy Verification

Clergy verification is a privileged trust label.

Rules:

- Users must not self-assert public clergy status.
- Only authorized administrators can grant `clergy_verified`.
- Parish admins may verify clergy only within the scope allowed by deployment policy.
- Diocesan admins or platform admins may be required for broader clergy verification.
- The verification record should state who verified the status, when, and within what scope.
- The system should support revocation or suspension of clergy verification.

Visible clergy status should show only after approval. It should not reveal sensitive notes or internal review details.

## Monastic Verification

Monastic verification is a privileged trust label.

Rules:

- Users must not self-assert public monastic status.
- Only authorized administrators can grant `monastic_verified`.
- Verification should be scoped to the monastery, parish, diocese, or platform policy that approved it.
- The verification record should state who verified the status, when, and within what scope.
- The system should support revocation or suspension of monastic verification.

Visible monastic status should show only after approval. It should not reveal sensitive notes or internal review details.

## Role-Based Room Access

Room access should be determined by policy, not by user self-labels.

Access inputs:

- Account approval state.
- Account suspension state.
- Parish membership.
- Group membership.
- Assigned roles.
- Explicit room membership.
- Verification status.

Example room policies:

| Room Type          | Allowed Access                                                            |
| ------------------ | ------------------------------------------------------------------------- |
| Parish general     | Active members, approved inquirers if parish policy allows it.             |
| Announcements      | Read access for members, post access for admins or approved announcers.    |
| Catechumen         | Inquirers, catechumens if modeled later, clergy, and assigned catechists.  |
| Clergy             | Users with `clergy_verified` and explicit room membership.                 |
| Monastic           | Users with `monastic_verified` and explicit room membership.               |
| Admin              | `parish_admin`, `diocesan_admin`, or `platform_admin` by scope.            |
| Shared inter-group | Explicit members approved by each participating group.                     |

Room access is visible to administrators through portal data and CLI output. User-facing room lists outside the admin UI are not implemented yet.

## Visible Verified Status

Visible verified status helps users know when an account has been reviewed.

Possible visible labels:

- Verified member
- Verified clergy
- Verified monastic
- Parish admin
- Diocesan admin

Visibility rules:

- `guest` and pending accounts should not show verified status.
- Clergy and monastic labels must appear only after manual verification.
- Internal verification notes must never be visible to ordinary users.
- Suspended users should not appear as active verified participants.
- The exact label text can be refined during UI design.

## Audit Trail

Verification and access decisions must create audit records.

Audited actions:

- Invitation created.
- Invitation revoked.
- Invitation accepted.
- Account approved.
- Account denied.
- Role assigned.
- Role removed.
- Parish or group membership added.
- Parish or group membership removed.
- Clergy verification granted.
- Clergy verification revoked.
- Monastic verification granted.
- Monastic verification revoked.
- Room access granted.
- Room access removed.
- Account suspended.
- Account restored.
- Account recovery started.
- Account recovery completed.

Audit records should include:

- Actor.
- Target user or resource.
- Action.
- Scope.
- Timestamp.
- Reason or note where needed.
- Source IP or session metadata if the deployment policy allows it.

Audit records should be append-only from the application perspective. Corrections should create new records instead of editing old records.

## Account Suspension

Suspension is for accounts that must lose access without immediate deletion.

Suspension effects:

- User cannot sign in to the portal.
- User cannot connect to Prosody.
- User cannot join rooms.
- User cannot join Jitsi meetings.
- User cannot start account recovery unless an administrator allows it.
- User should be removed from active room access until restored, or blocked by a suspension check.

Suspension records should include:

- Suspending administrator.
- Reason.
- Scope if suspension can be partial.
- Timestamp.
- Restoration administrator and timestamp if restored.

Deletion policy is unresolved and should be handled separately from suspension.

## Account Recovery

Account recovery must restore access only to the correct verified person.

Recovery flow:

1. User requests recovery through the approved recovery channel.
2. System records recovery request.
3. Administrator reviews the request if the account has trusted roles or verified status.
4. Recovery token or reset action is issued only after policy checks.
5. User resets credentials.
6. System records completion in the audit trail.

Recovery requirements:

- Suspended accounts should not self-recover by default.
- Accounts with `clergy_verified`, `monastic_verified`, `parish_admin`, `diocesan_admin`, or `platform_admin` should require stronger review.
- Recovery must not create a new verified identity without review.
- Recovery tokens should expire and be single-use.
- Recovery details must not expose whether a sensitive account exists to unauthenticated users.

## Conceptual Database Entities

These entities are represented by portal SQL migrations.

| Entity                  | Purpose                                                                  |
| ----------------------- | ------------------------------------------------------------------------ |
| User                    | Core account identity and login state.                                    |
| Invitation              | Invite token, creator, scope, expiration, and status.                     |
| Parish                  | Local parish, monastery, mission, or community boundary.                  |
| Group                   | Ministry, room-related group, or shared inter-group unit.                 |
| Membership              | User membership in a parish or group with state and scope.                |
| RoleAssignment          | Additive user role assignment with scope and timestamps.                  |
| VerificationRecord      | Manual verification decision for member, clergy, or monastic status.      |
| Room                    | Chat room or channel controlled by policy.                                |
| RoomAccessPolicy        | Rule linking rooms to roles, memberships, verification states, or users.  |
| RoomMembership          | Explicit user membership in a room where needed.                          |
| Suspension              | Account suspension state, reason, actor, and restoration details.         |
| RecoveryRequest         | Account recovery request, status, token metadata, and decision trail.     |
| AuditEvent              | Append-only record of invitations, approvals, roles, access, and recovery. |

## Administrative Scope

Administrative authority should be scoped.

- `parish_admin` acts within assigned parish or group boundaries.
- `diocesan_admin` may act across assigned parishes or diocesan groups.
- `platform_admin` may act across the instance for technical and emergency needs.
- Verification authority for clergy and monastics may require stricter policy than normal member approval.

The final scope model is open until the first real deployment requirements are known.

## Open Questions

- Who may grant `clergy_verified` in a single-parish deployment?
- Who may grant `monastic_verified` in a single-parish deployment?
- Should clergy and monastic verification always require two-person approval?
- Which recovery channel should be used for users without email?
- Should account deletion be supported in MVP, or only suspension and disablement?
- How long should audit records and verification notes be retained?
- Which verification labels should be visible in chat versus portal-only views?
- Should external XMPP clients see the same verified status as the web client?
