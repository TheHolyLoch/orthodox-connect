# Orthodox Connect Administrator Onboarding Guide

## 1. Admin Onboarding Goals

This guide gives new Orthodox Connect administrators a practical path for running the current MVP without weakening the trust model.

Goals:

- Keep registration invite-only.
- Keep clergy, monastic, and parish admin status manually reviewed.
- Keep privileged actions tied to named admin users.
- Keep room and meeting access based on portal roles, groups, and explicit membership.
- Keep public registration and open federation disabled.
- Keep secrets, invite tokens, meeting tokens, private notes, and backups out of Git.
- Keep audit records useful for later review.

This guide is for administrator workflow, not server installation. Host setup, DNS, TLS, backups, restore, and Docker operation remain technical operator responsibilities unless an admin also has that role.

## 2. Who This Guide Is For

This guide is for trusted people who manage users, groups, roles, rooms, meetings, and verification inside Orthodox Connect.

Administrator types:

| Role | Typical Scope |
| ---- | ------------- |
| `parish_admin` | A parish, monastery, mission, ministry, or assigned group. |
| `diocesan_admin` | A wider set of parishes, monasteries, missions, or groups where local policy grants that authority. |
| `platform_admin` | Instance-wide technical and emergency administration. |
| Technical operator | Host, Docker, DNS, TLS, restore, backups, and service health. |

An administrator should act only inside the scope assigned to that account. Admin accounts must not be shared.

## 3. Initial Admin Account Setup

The first admin account is created by the trusted deployment operator or another already-authorized administrator. Do not commit real admin usernames, passwords, reset links, or one-time setup tokens to the repository.

Initial checks:

- Confirm the account belongs to the intended person.
- Confirm the account has only the admin role it needs.
- Confirm the password is strong and not reused.
- Confirm the admin can reach the portal admin view.
- Confirm the admin can view users, groups, roles, invites, verification requests, rooms, and audit events.
- Confirm the admin cannot approve actions outside their assigned scope.
- Confirm there is a second trusted admin or operator path for emergencies where local policy allows it.

If the first admin account is wrong, stop onboarding and have the technical operator correct it before inviting users.

## 4. Understanding Roles and Permissions

Roles are additive. A user may be both a normal member and verified clergy, or both a parish admin and verified clergy.

Current role meanings:

| Role | Meaning |
| ---- | ------- |
| `guest` | Limited invited account before normal approval or membership. |
| `inquirer` | Approved limited account for catechism or early parish contact. |
| `member` | Normal verified parish or group member. |
| `parish_admin` | Local administrator for assigned parish, monastery, mission, ministry, or group scope. |
| `clergy_verified` | Clergy status approved through manual verification. |
| `monastic_verified` | Monastic status approved through manual verification. |
| `diocesan_admin` | Higher-scope administrator where local policy grants it. |
| `platform_admin` | Instance-wide technical and emergency authority. |

Rules:

- Users must not self-assign privileged roles.
- Clergy and monastic status must come from an admin decision.
- Parish admin status must come from an admin decision.
- Suspended users must not keep active room or meeting access.
- Chat names, display names, and meeting names are not proof of verified status.

## 5. Creating and Managing Invites

Invites are the start of account access. Use them deliberately.

When creating an invite, set:

- Creator admin.
- Expiry date.
- Scope, such as group, parish, monastery, mission, or guest purpose.
- Single-use by default.
- Reusable only when explicitly needed and reviewed.

Invite rules:

- Expired invites must not be accepted.
- Revoked invites must not be accepted.
- Already-used single-use invites must not be accepted.
- Invite redemption must not grant clergy, monastic, parish admin, diocesan admin, or platform admin status.
- Invite links should be sent through an approved out-of-band path.
- Invite links must not be pasted into public channels, logs, commits, issues, or documentation.

Review active and reusable invites regularly. Revoke unused invites that are no longer needed.

## 6. Reviewing Verification Requests

Verification requests are manual trust decisions.

Supported request types:

- `clergy`
- `monastic`
- `parish_admin`

Review steps:

1. Check the requesting user.
2. Check the requested verification type.
3. Check the relevant parish, monastery, mission, group, or diocesan scope.
4. Confirm the request through the approved local process.
5. Approve or reject the request.
6. Enter a short reason when rejecting.
7. Confirm the audit event was created.

Do not approve a request only because the user wrote the role in a display name or message. Do not approve your own privileged status.

## 7. Assigning Roles

Role assignment should follow verification and local authority.

Expected role assignment from verification:

| Verification Type | Role Assigned |
| ----------------- | ------------- |
| `clergy` | `clergy_verified` |
| `monastic` | `monastic_verified` |
| `parish_admin` | `parish_admin` |

Rules:

- Assign only the role needed.
- Keep `platform_admin` rare and limited to trusted operators.
- Keep `diocesan_admin` limited to approved wider-scope administrators.
- Correct mistakes by making a new action and keeping the audit trail.
- Revoke or suspend access when a trusted role should no longer apply.

Visible status should come from portal records, not from user-editable names.

## 8. Creating and Managing Groups and Parishes

Groups model parishes, monasteries, missions, ministries, shared groups, and admin scopes.

Before creating a group, decide:

- Display name.
- Short slug.
- Group type.
- Parent group, if any.
- Responsible admin.
- Whether membership is ordinary, restricted, or shared.

Membership states should be clear:

- `invited`
- `pending`
- `active`
- `suspended`
- `removed`

Group names can reveal sensitive information. Do not create names that expose pastoral, disciplinary, youth, monastic, or private details to people who should not know about them.

## 9. Creating and Managing Rooms and Channels

Rooms and channels should map to a real communication need.

Supported room scopes:

| Scope | Use |
| ----- | --- |
| `public_to_members` | Broad member room for approved members. |
| `group_only` | Room limited to members of a group. |
| `clergy_only` | Room limited to verified clergy. |
| `monastic_only` | Room limited to verified monastics. |
| `admin_only` | Room limited to approved administrators. |
| `invite_only` | Room limited to explicit room members. |

Room rules:

- Create rooms only under the right group or scope.
- Add room members only when access rules allow it.
- Do not expose private room names to unauthorized users.
- Keep sensitive room names plain and discreet.
- Review stale rooms and memberships regularly.
- Confirm room creation and membership changes appear in audit events.

Portal room policy remains the source of truth. Prosody room behavior must not override portal policy.

## 10. Managing Jitsi Meetings

Jitsi meetings are controlled by portal policy and JWT access.

Meeting rules:

- Meeting creation must remain role-gated.
- Anonymous public room creation must remain disabled.
- Meeting names alone must not grant access.
- Guests may join only when explicitly allowed.
- Guest access should be limited, expiring, and revocable.
- JWT secrets and token bodies must not be copied into notes, logs, issues, or documentation.
- Suspended users must not receive new meeting access.

When creating or reviewing a meeting, check:

- Creator user.
- Creator role.
- Meeting scope.
- Guest policy.
- Token expiry.
- Audit event for meeting creation or token issuance.

If a meeting link is shared too widely, revoke or rotate access per local policy and involve the technical operator if secrets may be exposed.

## 11. Viewing Audit Logs

Audit logs show who made trust and access decisions.

Review audit events for:

- Invite creation.
- Invite revocation.
- Invite redemption.
- Verification request creation.
- Verification approval.
- Verification rejection.
- Role assignment.
- Room creation.
- Room membership changes.
- Meeting creation.
- Meeting token issuance.
- Account suspension or restoration where supported.

Audit rules:

- Do not delete audit records to hide mistakes.
- Do not store passwords, JWTs, invite tokens, recovery tokens, or private keys in audit notes.
- Keep notes short and factual.
- Treat audit data as sensitive administrator data.

Corrections should create new records instead of editing history.

## 12. Handling User Issues

Common user issues:

| Issue | Admin Response |
| ----- | -------------- |
| Invite expired | Create a new invite if the person should still join. |
| Invite revoked | Confirm whether revocation was intentional before issuing another invite. |
| Invite already used | Check whether it was a single-use invite and whether the correct user redeemed it. |
| Account pending | Review the account and approve, deny, or leave pending per local policy. |
| Verification pending | Review the request through the approved process. |
| Missing room | Check account state, group membership, role, suspension state, and room scope. |
| Meeting denied | Check meeting scope, creator policy, guest setting, expiry, and user state. |
| Suspicious account | Suspend or restrict access if needed, then review audit and logs. |

Ask users for the minimum information needed. Do not ask users to send passwords, raw tokens, private keys, or full screenshots that expose private conversations.

## 13. Security Best Practices for Admins

Admin accounts carry trust. Treat them carefully.

Practices:

- Use a strong unique password.
- Do not share admin accounts.
- Use the lowest admin role that can do the work.
- Keep `.env`, backup files, JWT secrets, invite tokens, and private keys out of Git.
- Do not paste production logs into public support channels without review.
- Confirm public registration remains disabled.
- Confirm open federation remains disabled unless a later approved policy enables it.
- Confirm Jitsi authenticated meeting creation remains enabled.
- Confirm internal service ports are not exposed directly.
- Suspend accounts quickly when compromise is suspected.
- Revoke active invites if an invite leak is suspected.
- Ask the technical operator to rotate secrets if a secret may be exposed.

Do not use Orthodox Connect admin notes as a place for pastoral files, private confessions, or unrelated personal records.

## 14. Backup Awareness

Backups are a technical operator task, but administrators should know the basics.

Admins should know:

- Who is responsible for backups.
- Where backup status is checked.
- When the last successful backup ran.
- When the last restore test happened.
- Who can approve a production restore.
- What user data may be affected by restoring from an older backup.

Current local backup scope includes PostgreSQL portal data, Prosody data and config, Jitsi config and data where present, and reverse proxy data where managed by the stack.

Backup rules:

- Backup files must not be committed to Git.
- Backup output should be treated as sensitive.
- Restore should be tested on disposable or approved data before replacing production data.
- A restore must not silently bypass registration, verification, room access, suspension, or Jitsi authentication policy.

## 15. Troubleshooting Basics

Start with the smallest useful check and escalate when server access is needed.

Basic admin checks:

- Can the admin view the portal?
- Is the user active, pending, suspended, disabled, or removed?
- Is the invite valid, expired, revoked, or used?
- Does the user have the expected group membership?
- Does the user have the expected role?
- Does the room scope allow that user?
- Is the meeting link still valid?
- Is guest access explicitly allowed?
- Is there an audit event for the disputed action?

Escalate to the technical operator for:

- Portal unavailable.
- Chat unavailable.
- Jitsi unavailable.
- Reverse proxy or TLS problems.
- Database errors.
- Backup or restore problems.
- Suspected leaked secrets.
- Suspected host compromise.

Use fake or disposable test users when checking workflows. Do not create real users just to test a system problem.

## 16. Support Escalation Placeholder

Each deployment should maintain a private support escalation list outside this repository.

Suggested escalation roles:

- Primary parish or group admin.
- Secondary parish or group admin.
- Technical operator.
- Backup and restore operator.
- Security incident contact.
- Diocesan or higher-scope contact, if applicable.

Do not commit real names, emails, phone numbers, hostnames, credentials, domains, or emergency contacts to this document.

## 17. Rollback Plan

Rollback should protect trust records first.

If an admin workflow causes a problem:

1. Stop creating new invites for the affected scope.
2. Pause verification decisions for the affected scope.
3. Suspend or restrict affected accounts only when needed.
4. Preserve audit events and relevant operator notes.
5. Revoke leaked invites or meeting access.
6. Ask the technical operator to rotate secrets if token, JWT, database, or `.env` exposure is suspected.
7. Restore from backup only when the current data cannot be repaired safely.
8. After rollback, confirm users, roles, groups, room access, meeting access, and suspensions are correct.
9. Confirm public registration remains disabled.
10. Confirm open federation remains disabled.
11. Confirm Jitsi authenticated meeting creation remains enabled.
12. Record what was done through the normal admin or operator review process.

Rollback must not delete users, roles, groups, invites, verification records, rooms, meetings, audit events, backups, logs, or unrelated service data just to hide an error.
