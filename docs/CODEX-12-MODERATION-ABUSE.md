# Orthodox Connect Moderation and Abuse

## Moderation Goals

Moderation should protect parish, diocesan, monastic, and trusted community communication without turning Orthodox Connect into a public social network.

Goals:

- Keep communities invite-only and manually verified.
- Give administrators clear tools for reports, review, suspension, and room access changes.
- Keep moderation powers scoped by role and group.
- Preserve audit records for trust and access decisions.
- Avoid collecting more message content or personal data than needed.
- Keep public registration disabled.
- Keep federation disabled unless a later trusted federation policy is approved.
- Avoid automated moderation as a substitute for administrator judgment.

Moderation is administrative support for local community order. It is not a replacement for pastoral care, canonical process, law enforcement, or emergency response.

## Types of Abuse to Handle

Orthodox Connect should be prepared to handle:

- Spam or repeated unwanted messages.
- Harassment, threats, or intimidation.
- Impersonation of clergy, monastics, parish admins, or parish members.
- Attempts to self-assert privileged status.
- Invite link sharing outside the intended scope.
- Reusable invite misuse.
- Unauthorized room access attempts.
- Meeting link forwarding outside approved participants.
- Disruptive behavior in group rooms.
- Sharing private room content outside the approved group.
- Account compromise or suspicious login behavior.
- Attempts to bypass suspension or verification.
- Abuse involving trusted federation, if federation is enabled later.
- Abuse involving Tor access, if onion access is enabled later.
- Copyright or sensitive-document misuse in the later library phase.

The system should distinguish between ordinary support problems, local conduct issues, compromised accounts, and emergency safety issues.

## Reporting Workflow

Users should have a simple way to report abuse without exposing reports to ordinary room members.

Planned workflow:

1. User selects the account, room, meeting, invite, or event being reported.
2. User chooses a report category.
3. User writes a short description.
4. User may attach limited evidence if the deployment policy allows it.
5. Report is visible to authorized administrators for the relevant scope.
6. The system records report creation in the audit trail.
7. The reporting user can see that the report was received, unless policy requires confidential handling.

Report categories should include:

- harassment
- impersonation
- spam
- invite misuse
- room access issue
- meeting misuse
- account compromise
- sensitive content exposure
- other

Reports should not require users to decide which administrator has jurisdiction. The portal should route by room, group, parish, or instance scope where possible.

## Admin Review Workflow

Admin review should be deliberate and auditable.

Review workflow:

1. Administrator opens the report queue for their scope.
2. Administrator reviews report metadata and allowed evidence.
3. Administrator checks related audit events, role assignments, room membership, invite state, and suspension state.
4. Administrator chooses an action or marks the report as needing escalation.
5. Administrator records a short reason.
6. The system writes an audit event.
7. Affected users are notified only where policy allows and where notification does not increase risk.
8. Reports are closed, escalated, or left pending with a next-review note.

Possible outcomes:

- no action
- user warning outside the system
- invite revocation
- room membership removal
- room posting restriction
- temporary suspension
- permanent ban
- role removal
- verified status revocation
- meeting access revocation
- escalation to a higher-scope administrator

Administrators should avoid copying full message bodies into notes unless necessary for review.

## Role-Based Moderation Powers

Moderation powers must be scoped.

| Role              | Moderation Scope                         | Powers |
| ----------------- | ---------------------------------------- | ------ |
| room_moderator    | Assigned room only.                      | Remove users from the room, flag reports, request admin review. |
| group_moderator   | Assigned group rooms.                    | Review group reports, manage room membership within policy. |
| parish_admin      | Assigned parish or group.                | Manage invites, users, roles, verification requests, rooms, reports, and suspensions within scope. |
| diocesan_admin    | Assigned diocesan scope.                 | Review cross-parish reports, coordinate parish admins, handle escalations. |
| platform_admin    | Whole instance.                          | Emergency suspension, technical response, instance-wide access control. |

Future moderator roles should be added only when the portal can enforce scope clearly. Privileged roles must not be self-assigned.

## Room-Level Moderation Controls

Room controls should fit the room type and privacy level.

Controls:

- Remove a user from a room.
- Block a suspended user from rejoining.
- Restrict posting to named roles for announcement rooms.
- Require explicit membership for restricted and private rooms.
- Disable guest access for sensitive rooms.
- Freeze room membership during an incident.
- Rename or close a room if the name or membership list exposes sensitive information.
- Review room history retention before sharing rooms across groups.

Room-level action must not grant broader account powers. Removing a user from one room should not suspend the whole account unless an administrator records a separate suspension decision.

## Account Suspension Model

Suspension is the main account-level safety action.

Suspension effects:

- User cannot use the portal.
- User cannot connect to Prosody.
- User cannot join rooms.
- User cannot create or join Jitsi meetings.
- User cannot redeem new invites unless an administrator explicitly allows recovery or review.
- User loses visible active verified status while suspended.

Suspension records should include:

- Suspending administrator.
- Target user.
- Reason.
- Scope, if partial suspension is later supported.
- Start time.
- End time, if temporary.
- Restoration administrator and timestamp, if restored.

Deletion should remain separate from suspension. Permanent removal affects records, backups, and audit history and needs a separate retention policy.

## Temporary vs Permanent Bans

Temporary bans should be used when review is incomplete, risk is time-limited, or a cooling-off period is enough.

Temporary ban requirements:

- Clear expiration time.
- Reason recorded.
- Scope recorded.
- Automatic restoration only if the account remains otherwise valid.
- Admin review before restoring privileged roles if the case involved impersonation, compromise, or verified status.

Permanent bans should be used when continued access is unsafe or outside the community policy.

Permanent ban requirements:

- Reason recorded.
- Admin actor recorded.
- Related reports and audit events linked.
- Invites created by the banned account reviewed.
- Room memberships removed or disabled.
- Meeting access revoked.
- Recovery blocked unless a higher-scope administrator reopens the case.

Permanent bans should not delete audit records.

## Cross-Group Abuse Handling

Cross-group abuse happens when an incident affects more than one parish, group, room, monastery, or trusted server.

Handling model:

- Each group administrator handles users within their scope.
- Shared room administrators handle the shared room.
- Diocesan or platform administrators coordinate where scopes overlap.
- Reports involving clergy, monastic, parish admin, diocesan admin, or platform admin roles require higher-scope review.
- Shared inter-group rooms may be frozen while access is reviewed.
- External federation cases follow the trusted federation abuse process if federation is later enabled.

Cross-group action must not silently expand one administrator's authority. Escalation should be explicit and audited.

## Evidence and Audit Requirements

Evidence and audit records are different.

Audit records should track:

- Report creation.
- Report assignment.
- Report status changes.
- Invite revocation.
- Role changes.
- Verification revocation.
- Room access changes.
- Room membership changes.
- Account suspension and restoration.
- Meeting access revocation.
- Federation scope changes when implemented.

Evidence may include:

- Reporter statement.
- Reported user ID.
- Room ID.
- Message IDs, if available.
- Meeting ID.
- Invite ID.
- Timestamps.
- Limited screenshots or excerpts if policy allows.

Evidence rules:

- Store only what is needed.
- Avoid storing message bodies by default.
- Avoid private pastoral notes.
- Do not include passwords, invite tokens, recovery tokens, JWTs, session cookies, or full request bodies.
- Restrict evidence access to administrators assigned to the case.
- Include evidence in backups only if retention policy allows it.

Corrections should create new audit records instead of editing old audit records.

## Appeals Process

Appeals should provide a way to correct mistakes without letting suspended users bypass safety controls.

Appeal workflow:

1. User contacts the approved local administrator or recovery contact.
2. Administrator records the appeal request.
3. A different administrator reviews the appeal where practical.
4. Reviewer checks reports, audit records, suspension reason, and current risk.
5. Reviewer restores, modifies, or upholds the action.
6. The decision is recorded in the audit trail.

Appeal limits:

- Suspended users should not self-recover automatically.
- Privileged role restoration should require stronger review.
- Appeals involving clergy, monastic, parish admin, diocesan admin, or platform admin status should be escalated.
- Appeals should not reveal reporter identity unless policy allows it and risk has been reviewed.

## Privacy Considerations

Moderation data can become sensitive quickly.

Privacy rules:

- Collect the least evidence needed for review.
- Keep report notes short and factual.
- Do not turn moderation notes into pastoral records.
- Limit access to reports by scope.
- Avoid copying private room content into long-term records.
- Keep log retention short unless policy requires otherwise.
- Treat audit records, reports, screenshots, and exports as sensitive.
- Do not include reports in public support requests.
- Do not expose reporter identity to ordinary users.
- Do not expose internal verification notes during moderation.

Administrators should assume that reports, logs, and backups may reveal sensitive community metadata even when message bodies are not stored.

## Coordination Between Admins

Admin coordination should be structured and limited to people with authority for the case.

Coordination rules:

- Every report has a responsible administrator or review group.
- Escalation path is recorded.
- Urgent issues have a clear emergency contact.
- Admins do not share accounts.
- Admins record decisions in the portal instead of only in private chat.
- Sensitive cases avoid broad group discussion.
- Cross-group cases name the affected groups and responsible admins.
- Platform admins intervene only when local scope is insufficient or service safety is at risk.

For trusted federation later, each trusted server must have abuse contacts and agreed response expectations before shared rooms are enabled.

## Future Automation Options

Automation is future support only. It must not replace administrator judgment.

Possible future options:

- Rate limits for login, invite redemption, posting, and meeting token requests.
- Duplicate report grouping.
- Flagging repeated invite failures.
- Flagging repeated failed login attempts.
- Flagging sudden room join failures.
- Temporary automatic room freeze after severe abuse reports.
- Admin dashboard views for unresolved reports and suspended users.
- Local health alerts for abuse spikes.

Automation rules:

- No opaque automated bans.
- No automated clergy, monastic, or parish admin verification.
- No external moderation provider without privacy review.
- No message-content scanning without explicit policy review.
- Automated flags must create review tasks, not final decisions, unless emergency policy is approved.

## Rollback Plan

Rollback should reverse faulty moderation actions without deleting audit history.

Rollback steps:

1. Identify the moderation action to reverse.
2. Confirm the reversing administrator has scope.
3. Restore room access, role assignment, invite state, or account state only as needed.
4. Keep the original audit event.
5. Add a new audit event describing the reversal.
6. Notify affected administrators.
7. Notify affected users only where policy allows.
8. Review whether backups, logs, or evidence need retention changes.
9. Review whether the original rule, admin role, or workflow caused the error.

Rollback must not delete users, reports, audit events, room history, backups, or unrelated service data.
