# Orthodox Connect Training Materials

## 1. Training Goals

Training should help users and administrators use Orthodox Connect safely without needing to understand the underlying services.

Goals:

- Teach invite-only onboarding in plain language.
- Show users how to use chat, rooms, roles, badges, and meetings.
- Teach administrators how to handle invites, verification, room access, and incidents.
- Keep public registration and open federation clearly out of scope.
- Keep training aligned with the current MVP, not future features.
- Avoid exposing secrets, invite tokens, meeting tokens, private notes, or real contact details.
- Give local communities reusable material they can adapt for their parish, monastery, diocese, or group.

Training should reduce routine support questions while preserving the manual trust model.

## 2. Audience Types

### General Users

General users need the shortest path to joining and participating.

Training should cover:

- Receiving an invite.
- Creating an account.
- Waiting for approval where required.
- Finding available rooms.
- Sending messages.
- Joining approved meetings.
- Recognizing roles and badges.
- Basic account and device safety.

General user training should avoid technical terms such as XMPP, Prosody, BOSH, WebSocket, JWT, Caddy, Docker, and federation.

### Clergy

Clergy training should cover ordinary user actions plus role-specific expectations.

Training should cover:

- What verified clergy status means.
- How clergy verification is approved.
- Why display names are not proof of role.
- Which rooms may be clergy-only.
- How to join approved meetings.
- How to report suspicious impersonation or access problems.

Training must not suggest that users can self-assign clergy status.

### Parish Admins

Parish admins need practical workflow training.

Training should cover:

- Creating, listing, and revoking invites.
- Reviewing pending users.
- Reviewing verification requests.
- Assigning allowed roles.
- Managing groups, rooms, and memberships.
- Creating or reviewing approved meetings.
- Reading audit events.
- Escalating incidents to platform admins or technical operators.

Parish admin training should stress scope. A parish admin acts only within the assigned parish, monastery, mission, ministry, or group.

### Platform Admins

Platform admins need training on instance-wide risk and technical escalation.

Training should cover:

- Admin role boundaries.
- Security-sensitive settings.
- Backup and restore awareness.
- Incident containment.
- Secret rotation escalation.
- Public registration and federation checks.
- Jitsi authentication checks.
- Internal service exposure checks.
- Audit preservation.

Platform admin training should not replace technical operator runbooks, but it should show when to involve them.

## 3. Training Formats

### Written Guides

Written guides are the primary format for the MVP.

Suggested written guides:

- User onboarding guide.
- Chat and rooms quick guide.
- Meetings quick guide.
- Roles and badges quick guide.
- Parish admin quick guide.
- Verification review guide.
- Incident first-response guide.

Written guides should be short, printable, and easy to update when the portal changes.

### Short Videos Placeholder

Short videos are a future training format.

Possible later videos:

- Creating an account from an invite.
- Joining a room.
- Joining a meeting.
- Creating an invite.
- Reviewing a verification request.

No videos or media files are created in this stage. Video scripts should not include real users, real domains, real invite links, real meeting links, real secrets, or private data.

### Live Sessions Placeholder

Live training sessions may be useful for first rollout.

Possible sessions:

- User introduction session.
- Clergy and monastic access session.
- Parish admin workflow session.
- Platform admin and operator handover session.

Live session plans should include a test environment or fake data. Do not use production user records for demonstration unless the deployment owner has explicitly approved it.

## 4. Core Topics

### Using Chat

User training should explain:

- How to open the chat page.
- How to sign in.
- How to send a message.
- How to read recent room messages.
- How to use direct messages where local policy allows them.
- How to avoid sharing private information in the wrong room.
- How to report suspicious messages.

Training should state that chat access depends on account approval and room policy.

### Joining Rooms

Room training should explain:

- Rooms are visible only when the user has access.
- Some rooms are broad member rooms.
- Some rooms are limited to a group.
- Some rooms are clergy-only, monastic-only, admin-only, or invite-only.
- Missing rooms usually mean the account does not have the needed role, group membership, or explicit room membership.
- Suspended accounts lose room access.

Users should be told to ask a parish admin if an expected room is missing.

### Using Roles and Badges

Role and badge training should explain:

- Roles and badges come from portal approval.
- Display names do not prove someone is clergy, monastic, or an admin.
- Verified clergy and verified monastic status require manual review.
- Parish admin status requires admin approval.
- Suspended users should not appear as active trusted users.

Training should avoid making badges decorative or vague. Badges exist to support trust and access decisions.

### Joining Meetings

Meeting training should explain:

- Meeting access comes from approved links or portal-issued access.
- Meeting names alone do not grant access.
- Guests can join only when explicitly allowed.
- Links and tokens should not be forwarded without permission.
- If a meeting link fails, the user should contact the meeting organizer or parish admin.

Training must not suggest that anonymous users can create public meetings.

### Basic Security Practices

Security training should be plain and repeated.

Teach users to:

- Use a strong password.
- Keep account access private.
- Avoid sharing invite links publicly.
- Avoid forwarding meeting links without permission.
- Report suspicious messages or impersonation.
- Sign out on shared devices.
- Keep browser and device software updated.
- Ask an admin before trusting a role claim made only in a display name.

Admins should receive stricter security training because their accounts affect other users.

## 5. Admin Topics

### Invites

Admin training should cover:

- Creating invites with a clear purpose.
- Choosing expiry dates.
- Using single-use invites by default.
- Marking reusable invites only when there is a clear reason.
- Listing active, expired, revoked, and used invites.
- Revoking invites that are no longer needed.
- Checking audit events for invite actions.

Admins should never paste invite links into public rooms, public documents, public issues, or logs.

### Verification

Admin training should cover:

- Supported request types: `clergy`, `monastic`, and `parish_admin`.
- Reviewing account state before deciding.
- Confirming status through the approved local process.
- Approving only when the admin has scope.
- Rejecting with a short reason.
- Keeping internal notes private.
- Checking that approval assigns the correct role.
- Checking that decisions create audit events.

Training should state clearly that Orthodox Connect does not automate clergy or monastic verification.

### Room Management

Admin training should cover:

- Creating rooms only for a clear purpose.
- Choosing the correct room scope.
- Managing group membership before adding users to group-only rooms.
- Adding explicit members only when policy allows.
- Reviewing stale rooms and memberships.
- Keeping private room names discreet.
- Checking audit events for room changes.

Supported room scopes:

- `public_to_members`
- `group_only`
- `clergy_only`
- `monastic_only`
- `admin_only`
- `invite_only`

### Incident Handling

Admin training should cover first response, not full technical recovery.

Teach admins to:

- Suspend or restrict suspicious accounts where policy allows.
- Revoke leaked invites.
- Close or revoke unsafe meeting access.
- Preserve audit events and relevant notes.
- Avoid deleting records to hide mistakes.
- Avoid sharing logs or screenshots publicly.
- Escalate suspected secret exposure to the technical operator.
- Escalate host, DNS, TLS, backup, restore, database, Prosody, Jitsi, or reverse proxy issues to the technical operator.

Incident training should use fake examples and should not include real user cases.

## 6. Suggested Training Flow

Suggested rollout order:

1. Train platform admins and technical operators on the trust model, backups, incident response, and service limits.
2. Train parish admins on invites, verification, rooms, meetings, and audit events.
3. Train clergy and monastics on verified status, room access, meetings, and impersonation reporting.
4. Train general users on invite onboarding, chat, rooms, meetings, and basic security.
5. Run a small test onboarding group with fake or approved test accounts.
6. Review support questions and improve written guides.
7. Begin wider user onboarding only after admins can handle routine issues.

Each training round should state what is implemented now and what remains future scope.

## 7. Ongoing Education Plan

Training should be repeated when workflows or risk change.

Ongoing education should include:

- Short refresher notes after major releases.
- Admin review before new room scopes or meeting policies are used.
- Security reminders before high-attendance meetings.
- Invite hygiene reminders for parish admins.
- Verification review reminders for clergy, monastic, and parish admin requests.
- Backup and restore awareness reminders for platform admins.
- Updated guides after portal, chat, Jitsi, or backup behavior changes.

Do not train users on future features such as federation, Tor, IRC bridge, library integration, native mobile apps, push notifications, or automated moderation until those features are implemented and reviewed.

## 8. Documentation Linkage

Training materials should point to the existing documentation instead of duplicating every rule.

Useful source documents:

| Topic | Source |
| ----- | ------ |
| Project purpose | `docs/CODEX-00-PROJECT-BRIEF.md` |
| Architecture | `docs/CODEX-01-ARCHITECTURE.md` |
| Identity and verification | `docs/CODEX-03-IDENTITY-VERIFICATION.md` |
| Security model | `docs/CODEX-04-SECURITY-MODEL.md` |
| User onboarding | `docs/CODEX-43-USER-ONBOARDING-GUIDE.md` |
| Admin onboarding | `docs/CODEX-44-ADMIN-ONBOARDING-GUIDE.md` |
| Admin operations | `docs/CODEX-29-ADMIN-OPERATIONS.md` |
| Testing and validation | `docs/CODEX-15-TESTING-VALIDATION.md` |
| Backup and restore | `docs/CODEX-32-BACKUP-RESTORE-DESIGN.md` |
| Go-live checklist | `docs/CODEX-42-GO-LIVE-CHECKLIST.md` |

Training guides should be reviewed after these source documents change.

## 9. Feedback Collection

Feedback should improve training without collecting unnecessary private data.

Collect:

- Which step was unclear.
- Which guide or session was used.
- Whether the user was general user, clergy, parish admin, or platform admin.
- Whether the problem involved invites, verification, rooms, meetings, or account access.
- Suggested wording improvements.

Do not collect:

- Passwords.
- Invite tokens.
- Meeting tokens.
- JWTs.
- Session cookies.
- Private keys.
- `.env` values.
- Full private conversations.
- Private pastoral notes.

Feedback should be reviewed by the responsible admin or documentation maintainer before changes are made.

## 10. Rollback Plan

Training rollback means withdrawing or correcting inaccurate guidance.

Rollback steps:

1. Identify the inaccurate guide, video placeholder, session plan, or handout.
2. Remove or mark the material as withdrawn.
3. Correct any claim that describes unimplemented features as available.
4. Correct any claim that weakens invite-only registration, manual verification, room access, meeting access, or audit expectations.
5. Confirm no real contacts, domains, invite links, meeting links, screenshots, secrets, or private data were included.
6. Notify affected admins through the approved local path.
7. Update linked docs or training notes only where needed.
8. Preserve audit records and incident notes if bad training caused a security or access issue.

Rollback must not change application code, Docker services, portal data, Prosody data, Jitsi state, backups, logs, or unrelated documentation.
