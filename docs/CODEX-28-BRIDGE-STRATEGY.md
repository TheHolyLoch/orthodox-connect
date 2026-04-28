# Orthodox Connect Bridge Strategy

## 1. Bridge Goals

Bridges are optional future interoperability tools. They should help a deployment connect limited Orthodox Connect activity to existing communication channels without weakening the portal trust model.

Goals:

- Keep Orthodox Connect, Prosody, Converse.js, and the portal as the primary communication and trust model.
- Support narrow, reviewed interoperability where a parish, diocese, monastery, or trusted group has a real operational need.
- Keep bridge access scoped to specific rooms, groups, announcements, or fallback channels.
- Preserve invite-only onboarding, manual verification, role checks, room policy, suspension, and audit records.
- Make bridged identities visibly distinct from local portal-approved users.
- Avoid bridging sensitive rooms by default.
- Avoid collecting or copying more message content than needed.
- Keep bridges removable without disrupting portal, XMPP, Jitsi, backups, or audit records.

No bridge should be part of the MVP trust layer. Bridges must not approve users, verify clergy or monastics, grant roles, create official meetings, or replace portal audit records.

## 2. What Should Be Bridgeable

Only low-risk and explicitly approved use cases should be considered.

Possible bridgeable items:

| Item | Default |
| ---- | ------- |
| Read-only public or member announcements | Review |
| Non-sensitive member help rooms | Review |
| Operator incident coordination notices | Review |
| Existing IRC community migration channels | Review |
| Low-sensitivity shared group rooms | Review |
| Meeting reminders without access tokens | Review |
| Library collection announcements after library policy exists | Later |

Bridgeable content should meet all of these conditions:

- The room or channel has named administrators.
- The bridge direction is documented.
- Participants understand the bridge boundary.
- The bridged service has acceptable moderation controls.
- The bridge can be disabled quickly.
- Message retention and logging are reviewed.
- No raw invite links, recovery tokens, Jitsi JWTs, session cookies, passwords, or private notes are bridged.

## 3. What Should Not Be Bridgeable

Some spaces and workflows should not be bridged by default.

Denied bridge targets:

| Item | Reason |
| ---- | ------ |
| Clergy-only rooms | High impersonation and confidentiality risk. |
| Monastic-only rooms | High identity and privacy sensitivity. |
| Admin rooms | Contains trust, access, and operational decisions. |
| Pastoral or private rooms | Sensitive content and context. |
| Youth or child-related rooms | Requires stricter safety review. |
| Verification workflows | Decisions must remain portal-controlled. |
| Invite redemption | Must stay controlled by the portal. |
| Account recovery | Must not be exposed through bridge systems. |
| Jitsi token delivery | Tokens must stay short-lived and portal-issued. |
| Audit log streams | Audit access must remain admin-scoped. |
| Open public chat | Conflicts with the private invite-only model. |

Rules:

- Do not bridge rooms where membership itself is sensitive unless a later policy explicitly approves it.
- Do not bridge private message content by default.
- Do not bridge a service that cannot remove abusive users promptly.
- Do not use bridge membership as proof of Orthodox Connect membership.

## 4. IRC Bridge Placeholder

IRC bridging is deferred and should start, if ever, with non-sensitive text channels.

Possible uses:

- Migration from an existing IRC community.
- Text-only fallback for non-sensitive announcements.
- Operator support for users who already understand IRC.
- Disposable bridge tests before any production use.

Rules:

- IRC must not become the primary trust layer.
- IRC nicknames and channel operator status must not imply portal verification.
- NickServ registration, if used, proves only control of an IRC account.
- Do not bridge clergy, monastic, admin, pastoral, youth, or private rooms by default.
- Label IRC-originated users and messages where the target client supports it.
- IRC channel logs must be disabled by default or reviewed before retention.
- Public IRC channels must not receive Orthodox Connect private room content.

IRC bridge work must follow the IRC fallback and bridge design before implementation.

## 5. Matrix Bridge Placeholder

Matrix bridging is a possible future option, not a selected service.

Possible uses:

- Interoperability with a community that already operates a trusted Matrix homeserver.
- Temporary migration from Matrix to Orthodox Connect rooms.
- Read-only announcements into a controlled Matrix room.

Rules:

- Matrix users must not be treated as portal-approved Orthodox Connect users unless explicitly mapped and approved.
- Matrix room membership must not grant portal, Prosody, or Jitsi access.
- Matrix power levels must not grant Orthodox Connect roles.
- Matrix display names and badges must not imply verified clergy, monastic, or admin status.
- End-to-end encryption behavior must be reviewed before any Matrix bridge is used.
- Message history, edits, redactions, reactions, and attachments must be reviewed for privacy and retention risk.
- Federation behavior of the Matrix homeserver must be reviewed before any bridge is approved.

Matrix bridge support should wait until local room policy, account provisioning, moderation, and abuse reporting are stable.

## 6. Email Notification Bridge Placeholder

Email notification bridging may be useful for one-way notices, but it is not implemented.

Possible uses:

- Send announcement summaries to approved members.
- Notify administrators of pending invites, verification requests, reports, or backup failures.
- Send meeting reminders without tokens.
- Send account status notifications after portal login and email policy exist.

Rules:

- Email must not become public registration.
- Email delivery must not include raw invite tokens unless the invite delivery workflow explicitly approves it.
- Email must not include recovery tokens in logs or bridge records.
- Email must not include Jitsi JWT bodies.
- Email notifications should avoid sensitive room names and message bodies by default.
- Users should be able to understand which notifications are official and which are bridged copies.
- SMTP credentials must stay outside Git.

Email should be treated as a notification channel, not a chat authority or identity authority.

## 7. Read-Only Announcement Bridge Placeholder

Read-only announcement bridges are the lowest-risk bridge category when carefully scoped.

Possible directions:

| Direction | Use Case |
| --------- | -------- |
| Orthodox Connect to external read-only channel | Parish notices or outage notices. |
| External approved source to Orthodox Connect announcement room | Existing parish bulletin feed after review. |

Rules:

- Announcement bridges should be one-way by default.
- Posting authority must remain with approved portal roles.
- Bridged announcements should identify their source.
- Do not include private room names, invite links, recovery links, JWTs, or internal hostnames.
- Do not let replies in the external channel write back into Orthodox Connect unless separately reviewed.
- Keep announcement bridge failures visible to administrators.

Read-only bridges should still be audited when they affect official community communication.

## 8. Identity Mapping Requirements

Identity mapping is the hardest bridge problem and must be explicit.

Requirements:

- Portal users remain authoritative for Orthodox Connect identity.
- External accounts must be mapped to portal users only through administrator review.
- Mapping must record the external network, external account ID, portal user ID, approving administrator, scope, and timestamp.
- Users must not self-map into privileged Orthodox Connect roles.
- Suspended portal users must lose mapped bridge access where the bridge can enforce it.
- External account deletion or rename must trigger review before remapping.
- Reused external usernames must not automatically inherit old access.

Mapping states should include:

- pending
- approved
- revoked
- suspended
- expired

Unmapped bridge users should be visibly labeled as external or bridged and should not receive private room access by default.

## 9. Role and Permission Mapping

Role mapping must be conservative.

Rules:

- Portal roles may grant bridge access only after a bridge policy says so.
- External roles must not grant portal roles.
- External moderator status must not grant Orthodox Connect moderator status.
- External admin status must not grant `parish_admin`, `diocesan_admin`, or `platform_admin`.
- Room-level bridge permissions must be scoped to one room or channel where practical.
- Role revocation in the portal should remove derived bridge access.
- Suspended users must be removed from bridge access where enforceable.

Suggested mapping direction:

| Portal Policy | Bridge Effect |
| ------------- | ------------- |
| Approved member | May read or post in approved low-risk bridged rooms. |
| Group member | May access a matching group bridge if explicitly enabled. |
| Room moderator | May moderate bridged room only if bridge supports it and policy allows it. |
| Admin role | May manage bridge settings only within approved scope. |
| Suspended or disabled user | Bridge access revoked or blocked. |

Bridge policy must never be broader than portal policy.

## 10. Verification Badge Handling

Verification badges must remain portal-controlled.

Rules:

- Clergy, monastic, parish admin, diocesan admin, and platform admin labels must come from portal records.
- Bridge systems must not let external display names imitate verified badges.
- External service badges must not be imported as Orthodox Connect verification.
- If verified users appear through a bridge, the bridge must clearly distinguish portal-verified status from external account names.
- If the bridge cannot display verified status safely, it should omit verified badges instead of guessing.
- Bridge clients should show bridged users as bridged, remote, or external where possible.
- Screenshots of bridged status must not be used as proof of clergy or monastic verification.

Verification decisions must remain administrator-controlled in the portal and must continue to create audit events.

## 11. Logging and Audit Requirements

Bridge activity can expose room names, external account names, timestamps, and message metadata.

Operational logs may include:

- Bridge service start, stop, and errors when a bridge exists.
- Connection failures.
- Authentication failures.
- Message delivery failures.
- Rate limit or abuse events.
- External service API failures.

Audit events should include:

- Bridge approved or disabled.
- Bridge scope changed.
- External service connected or disconnected.
- External account mapped to a portal user.
- External account mapping revoked.
- Bridged room enabled or disabled.
- Bridge moderation action applied.
- Bridge failure that affects access or official communication.

Logs and audit metadata must not include:

- Passwords.
- Invite tokens.
- Recovery tokens.
- Jitsi JWT bodies.
- Session cookies.
- `.env` contents.
- Full request bodies.
- Private pastoral notes.
- Message bodies unless a reviewed evidence policy allows it.

Routine bridge logs should have short retention. Incident evidence should be restricted to authorized administrators.

## 12. Abuse and Moderation Risks

Bridges increase moderation complexity because abuse can cross system boundaries.

Risks:

- External users may not share Orthodox Connect identity standards.
- External services may allow weaker account names or easier impersonation.
- Moderation actions may not sync consistently.
- Deleted or edited messages may behave differently across systems.
- External channel logs may preserve messages after Orthodox Connect removes them.
- Abuse reports may need administrators from both sides.
- External systems may expose private room names or participants.
- Bridge outages may duplicate, delay, or reorder messages.

Controls:

- Start with one-way or low-risk bridge use.
- Bridge only named rooms.
- Require named administrators for each bridge.
- Keep abuse contacts for external services.
- Disable bridges quickly during incidents.
- Preserve portal audit events for access decisions.
- Keep sensitive rooms unbridged by default.

Moderation must remain administrator-driven. Bridges should not add opaque automated bans or message scanning without a later reviewed policy.

## 13. Security Risks

Bridge services expand the trusted computing base.

Security risks:

- Bridge credentials or API tokens may be leaked.
- External services may be compromised.
- External admins may have access to copied messages.
- Bridge software may store message content, attachments, or metadata.
- Attachments may bypass Orthodox Connect upload policy.
- External federation may spread messages beyond the approved scope.
- Bridge loops may create spam or denial-of-service conditions.
- Bridge logs may collect more data than the portal would collect.
- A compromised bridge may post misleading official notices.

Required controls before implementation:

- Separate bridge credentials per environment.
- Store bridge secrets outside Git.
- Scope bridge credentials to the minimum needed permissions.
- Disable attachment bridging by default.
- Disable sensitive room bridging by default.
- Rate limit bridge posting where possible.
- Test rollback with disposable data.
- Review backups for bridge data and secrets.
- Review external service retention and deletion behavior.

If the bridge cannot be secured to a clear scope, it should not be deployed.

## 14. Rollback Plan

Bridge rollback must remove interoperability without damaging Orthodox Connect data.

Rollback steps:

1. Disable the affected bridge.
2. Revoke bridge credentials or API tokens if exposure is suspected.
3. Remove bridge route, room, or channel references from user guidance.
4. Confirm portal, Prosody, Converse.js, Jitsi, backups, and reverse proxy still work.
5. Confirm public registration remains disabled.
6. Confirm open federation remains disabled unless separately approved.
7. Confirm portal roles, verification, room access, and suspension state remain authoritative.
8. Preserve portal audit events and incident notes.
9. Review external service logs and retained messages for sensitive exposure.
10. Remove external account mappings or mark them revoked where needed.
11. Notify affected administrators through an approved contact path.
12. Decide whether the bridge can be restored, reduced to read-only, or retired.

Rollback must not delete portal users, roles, groups, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
