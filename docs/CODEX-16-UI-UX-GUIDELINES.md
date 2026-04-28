# Orthodox Connect UI/UX Guidelines

## UX Goals

The portal and chat experience should make Orthodox Connect usable by ordinary parish, diocesan, monastic, and community members without requiring technical knowledge.

Goals:

- Keep onboarding invite-only and clear.
- Make account state visible without exposing private admin notes.
- Help users find approved rooms and meetings quickly.
- Keep clergy, monastic, parish admin, and platform admin labels tied to verified portal data.
- Keep privileged actions deliberate, scoped, and auditable.
- Keep chat, portal, and meeting entry points visually consistent.
- Avoid protocol language in user-facing screens unless it is needed for troubleshooting.
- Prefer simple pages, short forms, and obvious next steps over dense dashboards.

The interface should reduce support burden for local administrators while preserving the security model.

## Target User Skill Level

The primary user is non-technical.

Assumptions:

- Users may be comfortable with email, parish websites, messaging apps, and video meeting links.
- Users should not need to understand XMPP, Prosody, Converse.js, BOSH, WebSocket, JWT, Docker, Caddy, federation, or TLS.
- Administrators may be parish staff or trusted volunteers, not full-time system operators.
- Technical maintainers need accurate service and audit views, but ordinary users should not see operator details.

UI text should use local community language such as invite, account, approval, room, meeting, parish, group, member, clergy, monastic, and administrator.

## First-Time User Journey

The first supported journey is invite-based.

Preferred flow:

1. User receives an invite from a trusted administrator through an approved out-of-band path.
2. User opens the invite link.
3. User sees the community name, what the account is for, and the next action.
4. User creates account credentials.
5. User sees account status, such as pending approval or approved.
6. User submits verification only if they need clergy, monastic, or parish admin status.
7. User sees available rooms after approval.
8. User enters chat through the web chat frontend.
9. User opens meeting links only when the portal grants access.

The first session should avoid showing empty admin concepts, system internals, or unavailable future features.

## Invite Onboarding Flow

Invite onboarding should be short and explicit.

User-facing requirements:

- Show whether the invite is valid, expired, revoked, or already used.
- Explain that access is invite-only.
- Explain that approval may be required before normal chat or meeting access.
- Ask only for information needed to create the account.
- Avoid asking users to choose roles.
- Avoid showing raw invite tokens after redemption.
- Give a clear next screen after redemption.

Administrator requirements:

- Invite creation should show expiry and single-use or reusable state.
- Reusable invites should be visibly marked.
- Revoked invites should be visibly marked.
- Invite lists should show creator, status, expiry, and redemption state.
- Invite actions should create audit events.

## Verification Flow

Verification is a manual administrator workflow.

Supported verification types:

- clergy
- monastic
- parish_admin

User flow:

1. User submits a request for one supported verification type.
2. User provides a short note if the local policy asks for it.
3. User sees the request status.
4. User cannot approve, reject, or edit the decision.
5. User sees approved verified status only after an administrator approves the request.

Administrator flow:

1. Admin reviews pending requests.
2. Admin approves or rejects the request.
3. Approved requests assign the matching role.
4. Rejected requests store a reason.
5. Every decision is tied to the admin user.
6. Every decision creates an audit event.

Internal verification notes must be visible only to authorized administrators.

## Role Visibility

Visible roles should help users recognize trust and responsibility without letting display names imitate authority.

Suggested labels:

| Role Data           | User-Facing Label |
| ------------------- | ----------------- |
| `member`            | Member            |
| `clergy_verified`   | Verified Clergy   |
| `monastic_verified` | Verified Monastic |
| `parish_admin`      | Parish Admin      |
| `diocesan_admin`    | Diocesan Admin    |
| `platform_admin`    | Platform Admin    |

Rules:

- Verified labels must come only from portal roles or verification records.
- Pending users should not show verified labels.
- Suspended users should not appear as active verified users.
- User-editable display names must not look like verified labels.
- External or future federated accounts must be clearly marked if federation is enabled later.
- Native XMPP clients may not show these labels, so the portal remains the source of truth.

Badges should be small, plain, and consistent. They should not dominate names or room lists.

## Room and Channel Navigation Model

Room navigation should reflect access policy.

Room scopes:

- `public_to_members`
- `group_only`
- `clergy_only`
- `monastic_only`
- `admin_only`
- `invite_only`

Navigation rules:

- Show only rooms the user may access.
- Give restricted rooms plain labels, not internal policy names.
- Separate broad rooms, group rooms, and restricted rooms if the list grows.
- Keep room descriptions short.
- Do not expose private room names to users without access.
- Show clear empty states when a user has no available rooms.
- Suspended users should not see active room navigation.

Administrators should be able to view room policy, membership, and audit events from the portal.

## Cross-Group and Channel Discovery UX

Cross-group discovery is conservative.

Current behavior should assume local rooms and explicitly shared rooms only. Future federation or shared inter-group channels must not create broad room browsing by default.

Discovery rules:

- Users should see only groups and rooms they are approved to know about.
- Shared rooms should identify the participating group or scope.
- Shared rooms should not imply access to either group's other rooms.
- Remote or federated rooms should be clearly marked if federation is enabled later.
- Clergy, monastic, admin, youth, private, or pastoral room names should not appear in public discovery.

If there is uncertainty, hide the room and let an administrator grant explicit access.

## Jitsi Meeting UX Integration

Meeting access should feel like part of the portal policy, not a public meeting link service.

User-facing rules:

- Users open meetings from portal-approved links or allowed rooms.
- Meeting creation is visible only to approved roles.
- Guests join only where explicitly allowed.
- Meeting names alone must not imply access.
- Expired or denied meeting links should show a clear access message.
- Users should not see JWTs, token contents, or service internals.

Administrator rules:

- Meeting creation should show who created the meeting.
- Token issuance should be auditable.
- Guest access should be explicit and limited.
- Public anonymous meeting creation must remain unavailable.

Jitsi mobile access should use the same approved links and role checks as desktop.

## Mobile UX Considerations

Mobile browser support is the first required mobile path.

Mobile requirements:

- Invite redemption fits narrow screens.
- Account status pages are readable on phones.
- Chat entry is easy to find after approval.
- Room lists and meeting links are usable without horizontal scrolling.
- Admin tables degrade into readable rows or compact lists.
- Verification review remains possible for administrators on a phone, but bulk admin work can remain desktop-oriented.
- Destructive admin actions require clear confirmation.

Native mobile XMPP clients are planned, not part of the current implemented support path. Setup instructions should be added only after client testing and Prosody account provisioning exist.

## Accessibility Considerations

The interface should follow basic accessibility expectations from the start.

Requirements:

- Use readable font sizes.
- Keep strong contrast for text and controls.
- Do not rely on color alone for status.
- Use labels for form fields.
- Keep focus order logical.
- Make buttons and links distinct.
- Provide clear error messages near the relevant field.
- Keep badges readable by screen readers.
- Avoid icon-only actions unless the action has an accessible name.
- Keep confirmation screens usable by keyboard.

Accessibility is part of making the system usable for parish and monastic communities, not a later cosmetic step.

## Error Handling UX

Errors should explain the next safe action without exposing sensitive details.

User-facing examples:

| Situation              | Message Direction |
| ---------------------- | ----------------- |
| Expired invite         | Say the invite expired and to ask the administrator for a new one. |
| Revoked invite         | Say the invite is no longer valid. |
| Used single-use invite | Say the invite was already used. |
| Pending approval       | Say the account is waiting for administrator review. |
| Missing room access    | Say the room is not available to this account. |
| Suspended account      | Say the account cannot access the service and to contact an administrator. |
| Meeting denied         | Say the meeting is not available to this account or link. |

Do not expose stack traces, database errors, JWT details, internal hostnames, tokens, or raw service responses to ordinary users.

## Minimal Design Principles

The design should be quiet, functional, and consistent.

Principles:

- Use one clear primary action per screen where practical.
- Keep forms short.
- Use tables for admin review when scanning matters.
- Use simple status labels for users, invites, verification requests, rooms, and meetings.
- Keep navigation stable.
- Keep wording plain.
- Use confirmation for irreversible or privileged actions.
- Prefer progressive disclosure over showing every admin field at once.
- Keep ordinary user screens separate from admin screens.
- Keep portal, chat, and meeting entry points visually connected through names and links.

The interface should look maintained and trustworthy, not promotional.

## Things to Avoid

Avoid:

- Public registration.
- Self-assigned clergy, monastic, parish admin, or platform admin status.
- Technical protocol names in ordinary user flows.
- Broad dashboards for new users.
- Hidden role changes.
- Ambiguous verified labels.
- Making invite links look reusable when they are single-use.
- Showing private room names to users without access.
- Exposing verification notes to ordinary users.
- Treating federation, Tor, IRC, library access, native mobile apps, or push notifications as implemented features.
- Marketing-style pages where the user needs a working portal, chat, or admin tool.
- Dense copy that makes local administrators explain the interface by hand.

Complexity should appear only where administrator judgment actually requires it.

## Rollback Plan

UI changes should be reversible without changing trust records.

Rollback steps:

1. Revert the faulty UI text, template, route, or view.
2. Confirm invite redemption still works.
3. Confirm admin-only verification decisions still require admin roles.
4. Confirm room lists still follow access policy.
5. Confirm Jitsi meeting creation remains role-gated.
6. Confirm public registration remains unavailable.
7. Confirm audit events are still recorded for privileged actions.
8. Preserve existing users, roles, invites, verification records, rooms, meetings, and audit events.

Rollback must not delete portal data, Prosody data, Jitsi state, backups, logs, or unrelated service configuration.
