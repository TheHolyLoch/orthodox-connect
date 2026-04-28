# Orthodox Connect Administrator Operations

## Admin Operation Goals

Administrator operations should keep Orthodox Connect stable, private, invite-only, and auditable.

Goals:

- Keep public registration disabled.
- Keep open federation disabled unless a later approved trusted federation plan enables it.
- Keep clergy, monastic, parish admin, diocesan admin, and platform admin status administrator-controlled.
- Keep room and meeting access derived from portal users, roles, groups, and explicit membership.
- Record privileged decisions in audit events.
- Keep secrets, raw tokens, private notes, and real domains out of Git and public documentation.
- Make routine operations clear enough for parish, diocesan, monastic, and technical administrators to follow.
- Preserve backups, audit records, and logs needed for recovery and incident review.

Administrator work should be scoped. An administrator should act only within the role, group, parish, monastery, diocese, or platform authority assigned to that account.

## Admin Role Types

Current and planned administrator roles:

| Role                 | Status                   | Scope |
| -------------------- | ------------------------ | ----- |
| `parish_admin`       | Current                  | Local parish, monastery, mission, ministry, or assigned group scope. |
| `diocesan_admin`     | Current                  | Higher-scope review across assigned parishes, monasteries, missions, or groups. |
| `platform_admin`     | Current                  | Instance-wide technical and emergency authority. |
| `room_moderator`     | Future                   | Assigned room only, after moderation tooling exists. |
| `group_moderator`    | Future                   | Assigned group rooms only, after moderation tooling exists. |
| Technical operator   | Current operational role | Host, Docker, backups, restore, DNS, TLS, and deployment operations. |
| Read-only auditor    | Future                   | Limited audit review where local policy requires separation of duties. |

Operational rules:

- Admin accounts must not be shared.
- Privileged roles must not be self-assigned.
- Verification decisions must be tied to an admin user.
- Technical operators should not change pastoral, clergy, monastic, or group trust decisions unless they also have the correct portal role.
- Emergency actions should be recorded in the portal audit trail or operator notes as soon as the system is available.

## Daily Admin Tasks

Daily checks should be short and focused on pending work and obvious service problems.

Tasks:

- Review pending invite redemptions.
- Review pending verification requests.
- Review users in `pending`, `suspended`, or unexpected states.
- Check recent audit events for unexpected privileged actions.
- Check that portal, chat, Prosody browser transports, Jitsi, PostgreSQL, and the reverse proxy are running.
- Check for repeated failed login, invite redemption, or meeting token attempts where those logs exist.
- Respond to user support requests through the approved local contact path.
- Confirm public registration and open federation have not been enabled.

Daily review should avoid opening private logs or sensitive records unless there is a reason.

## Weekly Admin Tasks

Weekly checks should catch drift before it becomes an incident.

Tasks:

- Review active, expired, revoked, and reusable invites.
- Revoke unused invites that are no longer needed.
- Review room and group memberships for stale access.
- Review official meetings, guest access, and old active meeting records.
- Check backup output age and recent backup success.
- Review reverse proxy, Prosody, Jitsi, and portal logs for repeated errors.
- Review admin role assignments and recent privileged changes.
- Confirm no internal service ports have been exposed outside the approved deployment model.
- Confirm no real secrets, backup files, logs, or generated service data have been added to Git.

Reusable invites should be rare, explicit, expiring, and reviewed weekly while active.

## Monthly Admin Tasks

Monthly checks should focus on readiness and access review.

Tasks:

- Run a restore test against disposable or approved data.
- Review platform, diocesan, and parish admin accounts.
- Review suspended and disabled accounts.
- Review room list, meeting list, and group list for stale or unclear records.
- Review backup storage location, free space, and retention.
- Review `.env.example`, local `.env`, and deployment notes for missing variables or stale instructions.
- Review whether any secret should be rotated per local policy.
- Review production documentation against the deployed service behavior.
- Confirm trusted federation, Tor onion access, IRC bridge, and library service remain disabled unless a later approved implementation enables them.

Monthly restore testing should record the backup timestamp, target environment, checks performed, and result.

## User Onboarding Procedure

User onboarding remains invite-only.

Procedure:

1. Authorized admin creates an invite with a clear scope, expiry, creator, and reusable setting.
2. Admin delivers the invite through an approved out-of-band path.
3. User redeems the invite.
4. Portal creates a pending user and records invite redemption.
5. Admin reviews the user by local parish, diocesan, monastic, or group policy.
6. Admin approves, denies, or leaves the account pending.
7. Admin assigns group membership and ordinary roles only where policy allows.
8. Admin records or confirms the audit event.

Rules:

- Public signup remains unavailable.
- Single-use invites should be the default.
- Reusable invites must be explicitly marked and reviewed.
- Expired, revoked, and already-used single-use invites must not create active access.
- Invite redemption alone must not grant clergy, monastic, parish admin, diocesan admin, or platform admin roles.
- Prosody account provisioning remains separate until implemented.

## Clergy and Monastic Verification Procedure

Clergy and monastic verification are manual trust decisions.

Procedure:

1. User submits a verification request for `clergy` or `monastic`.
2. Authorized admin reviews the request, account state, group scope, and local verification policy.
3. Admin confirms the status through approved local or diocesan channels outside the platform where needed.
4. Admin approves or rejects the request.
5. Approved requests assign the matching verified role.
6. Rejected requests store a reason.
7. Portal records an audit event tied to the deciding admin.

Rules:

- Users cannot approve their own requests.
- Users cannot self-assign clergy or monastic status.
- Internal verification notes must stay admin-only.
- Visible verified labels should come from portal state, not chat nicknames or Jitsi names.
- Revocation or correction should create a new audit event rather than deleting history.
- Suspended users should lose active verified status while suspended.

## Room and Channel Management Procedure

Rooms and channels should be created only when there is a clear group, parish, monastic, clergy, admin, or meeting need.

Procedure:

1. Authorized admin creates a room record in the portal.
2. Admin assigns an owning group where needed.
3. Admin selects the room scope.
4. Admin adds explicit room members only where access rules allow.
5. Admin reviews the room name for privacy and clarity.
6. Admin confirms room access with portal data.
7. Portal records audit events for creation and membership changes.

Supported scopes:

- `public_to_members`
- `group_only`
- `clergy_only`
- `monastic_only`
- `admin_only`
- `invite_only`

Rules:

- Room access must be derived from account state, group membership, roles, explicit room membership, and suspension state.
- Sensitive room names should not expose pastoral, clergy, monastic, youth, or private details to unauthorized users.
- Suspended users must not retain active room access.
- Prosody MUC synchronization remains a derived service concern and must not override portal policy.
- Shared inter-group rooms require explicit membership and named responsible admins.

## Jitsi Meeting Management Procedure

Jitsi meetings are official meeting records controlled by portal policy.

Procedure:

1. Approved creator requests or creates a meeting through the portal workflow.
2. Portal checks creator role, user status, room access, group scope, and meeting policy.
3. Admin or creator sets meeting name, scope, guest policy, and expiry where supported.
4. Portal issues meeting links or JWT access only after policy checks.
5. Guests are approved explicitly where guest access is allowed.
6. Old or cancelled meetings are closed.
7. Portal records meeting creation and token issuance metadata in audit events.

Rules:

- Anonymous public room creation remains disabled.
- Meeting creation remains role-gated.
- Meeting names must not grant access by themselves.
- Guest access must be explicit, expiring, and revocable.
- JWT secrets and token bodies must not be logged, copied into notes, or committed.
- Suspended users must not receive new meeting tokens.

## Backup Check Procedure

Backups are local filesystem backups for the current stage.

Procedure:

1. Confirm `.env` exists on the host and is not committed.
2. Run or review the backup script per local operating policy.
3. Confirm a timestamped backup directory or archive was created.
4. Confirm PostgreSQL data is included.
5. Confirm Prosody data and configuration are included.
6. Confirm Jitsi configuration and data are included where present.
7. Confirm reverse proxy data is included where managed by the stack.
8. Confirm backup output is excluded from Git.
9. Review the backup manifest for completeness without exposing secret values.
10. Test restore on a disposable or approved target on the monthly schedule.

Rules:

- Backups must be protected like sensitive community records.
- Backup files must not be committed to Git.
- Backup logs and manifests must not print `.env` contents, database passwords, JWT secrets, invite tokens, recovery tokens, session cookies, or private keys.
- Production restores should be tested on a safe target before replacing live data unless there is an emergency.

## Log Review Procedure

Log review should find service problems and abuse signals without collecting unnecessary private data.

Procedure:

1. Review portal audit events first for trust and access decisions.
2. Review service logs only for the affected time range or weekly operational window.
3. Check reverse proxy errors, upstream failures, and TLS renewal problems.
4. Check Prosody authentication, transport, and MUC errors.
5. Check Jitsi JWT, meeting join, Jicofo, and JVB errors.
6. Check backup and restore script output.
7. Record significant findings in operator notes or audit records where supported.

Never store or copy into notes:

- Passwords.
- Session cookies.
- JWT secrets or token bodies.
- Invite tokens.
- Recovery tokens.
- Message bodies.
- Private room contents.
- Full request bodies.
- `.env` contents.
- TLS, onion, or backup private keys.

Logs should have short retention unless a deployment has a documented reason to keep them longer.

## Incident Handling Procedure

Incidents should be handled by containing risk first, then preserving records and repairing access.

Procedure:

1. Identify the affected service, account, room, invite, meeting, route, or secret.
2. Contain the issue by suspending accounts, revoking invites, closing meetings, or disabling affected routes where needed.
3. Preserve relevant logs, audit events, backup manifests, and operator notes.
4. Review scope, affected users, affected groups, and exposed data.
5. Rotate exposed or suspected secrets.
6. Restore from backup only if data integrity cannot be repaired safely.
7. Notify approved administrators and affected users through the approved local path.
8. Record final action and follow-up review.

Rules:

- Do not delete audit records to hide mistakes.
- Do not turn incident notes into pastoral or personal files.
- Do not publish real domains, secrets, invite links, meeting tokens, or private host details in public support requests.
- Emergency decisions made outside the portal should be recorded when the portal is available.
- If identity data cannot be trusted, keep chat and meetings offline until portal roles, suspensions, and room access are reviewed.

## Account Suspension Procedure

Suspension is the normal account-level safety action.

Procedure:

1. Authorized admin identifies the target account and reason.
2. Admin confirms the action is within scope.
3. Admin records the suspension reason and expected duration where known.
4. Portal marks the user suspended.
5. Admin reviews active room memberships, meeting access, guest records, and invites created by the account.
6. New Jitsi token issuance is stopped for the suspended user.
7. Prosody access is disabled when provisioning sync exists.
8. Portal records an audit event.

Rules:

- Suspended users should not access the portal, chat, rooms, meetings, invite redemption, or account recovery unless a reviewed recovery path allows it.
- Suspension should not hard-delete audit history.
- Temporary suspensions should include an expiration or review date.
- Permanent bans should still preserve records needed for review.
- Restoring a privileged user should require stronger review than restoring an ordinary account.

## Trusted Federation Admin Procedure Placeholder

Trusted federation is not enabled by default.

Future procedure before enabling any trusted server:

1. Record the federation request.
2. Verify the remote server identity, operator, admin contacts, hostname, and XMPP domain.
3. Define the smallest allowed federation scope.
4. Agree on abuse handling, revocation, logging, and emergency contacts.
5. Test with non-sensitive rooms first.
6. Record approval in audit events or operator notes.
7. Review the relationship on a regular schedule.

Rules:

- Do not invent or preapprove trusted partner servers.
- Open federation remains disabled.
- Remote clergy or monastic verification does not automatically grant local access.
- Revocation should remove remote users from shared rooms and preserve audit records.

## Tor and Onion Admin Procedure Placeholder

Tor onion access is not enabled in the current MVP.

Future procedure before enabling onion access:

1. Decide which services should have onion endpoints.
2. Limit onion access to portal and chat unless a later review approves more.
3. Keep Jitsi media, PostgreSQL, Docker, host admin, and internal service ports off onion routes.
4. Protect onion private keys as secrets.
5. Apply the same authentication, authorization, suspension, and audit rules as public HTTPS routes.
6. Add rate limits and abuse review appropriate for onion traffic.
7. Write user guidance for Tor Browser.
8. Test rollback before sharing an onion hostname.

Rules:

- Onion access must not bypass portal login, admin roles, verification, room access, or meeting token checks.
- Onion hostnames and onion private keys must not be committed.
- If abuse increases, onion access should be reduced or disabled until reviewed.

## Rollback Plan

Administrative rollback should reverse unsafe operational changes without deleting trust records.

Rollback steps:

1. Identify the admin action, service change, invite, role, verification decision, room access change, meeting, or suspension to reverse.
2. Confirm the reversing admin has scope.
3. Preserve audit events and relevant logs before making repairs.
4. Revoke unsafe invites, roles, memberships, meeting links, or tokens.
5. Restore removed access only when current policy allows it.
6. Add corrective audit events instead of deleting original records.
7. Restore from backup only if data integrity cannot be repaired safely.
8. Rotate secrets if rollback follows exposure.
9. Confirm public registration remains disabled.
10. Confirm open federation remains disabled.
11. Confirm Jitsi authentication remains enabled.
12. Confirm admin routes still require admin roles.
13. Confirm backups and logs remain protected.

Rollback must not delete users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
