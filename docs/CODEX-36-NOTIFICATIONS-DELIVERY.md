# Orthodox Connect Notifications and Delivery

## 1. Notification Goals

Notifications should help approved users and administrators notice relevant activity without weakening privacy, access control, or the invite-only trust model.

Goals:

- Keep primary chat delivery inside XMPP and Converse.js.
- Keep portal workflow notifications tied to portal users, roles, groups, rooms, meetings, and audit events.
- Avoid exposing private room names, message bodies, invite tokens, recovery tokens, JWT bodies, or admin-only notes.
- Let users control how much non-critical activity they see.
- Alert administrators about trust, access, backup, and service issues without adding external providers in the MVP.
- Keep public registration disabled.
- Keep open federation disabled unless a later trusted federation release enables it.
- Keep Jitsi meeting creation authenticated and role-gated.
- Fail safely when notification delivery is unavailable.

Notifications are supporting signals. They must not grant access, approve users, verify roles, create meetings, or replace audit records.

## 2. Types of Notifications

Orthodox Connect should separate ordinary user notifications from administrator alerts.

| Type                 | Primary Audience       | Source                         | Current Direction |
| -------------------- | ---------------------- | ------------------------------ | ----------------- |
| direct messages      | Approved users          | XMPP client and Prosody         | Current XMPP behavior |
| mentions             | Approved users          | XMPP room clients               | Current or client-dependent |
| room activity         | Approved users          | XMPP rooms                      | Current or client-dependent |
| verification updates | Users and admins        | Portal verification workflow    | Portal placeholder |
| invite events         | Admins and invited users | Portal invite workflow          | Portal placeholder |
| admin alerts          | Admins and operators    | Portal, logs, backups, services | Manual or future |

Direct message notifications:

- Should depend on the user's approved XMPP account and client.
- Must stop when the user is suspended or disabled.
- Must not treat display names as proof of verified status.

Mention notifications:

- Should respect room membership and visibility.
- Should not notify users about rooms they cannot access.
- Should avoid leaking sensitive room names in external channels.

Room activity notifications:

- Should be user-controlled where the client supports it.
- Should default to conservative behavior for high-volume rooms.
- Should be minimized for clergy, monastic, admin, youth, pastoral, or private rooms unless local policy approves previews.

Verification update notifications:

- May notify a user that a request was received, approved, or rejected.
- Must not expose internal verification notes to ordinary users.
- Must record decisions through audit events.

Invite event notifications:

- May notify admins that invites were created, redeemed, revoked, expired, or abused.
- Must not send raw invite tokens through logs or unreviewed external channels.
- Must preserve single-use and expiry rules.

Admin alerts:

- May cover pending verification, suspicious invite use, failed backups, service outage, repeated auth failures, and unexpected privileged actions.
- Must be visible only to authorized admins or operators.
- Must not include secrets or full request bodies.

## 3. In-App Notification Model

In-app notifications are the preferred first portal notification layer.

Model:

- Portal stores notification-like state only for portal workflows that need review.
- Admin pages show pending work such as invite redemptions, verification requests, room changes, meeting requests, and audit events.
- User pages show account status, verification request status, available rooms, and available meetings.
- Chat activity stays in Converse.js and Prosody rather than being duplicated into portal records.

In-app notification rules:

- Require authentication for private notification views.
- Scope admin notifications by role and group.
- Do not show private rooms to users without access.
- Do not expose raw invite tokens after creation.
- Do not expose Jitsi JWT bodies.
- Do not expose internal verification notes to ordinary users.
- Use audit events for trust and access decisions, not notification records.
- Treat notification state as derived from source records where practical.

In-app notifications should be enough for MVP administrator review. Email, push, and external alerting are later additions.

## 4. Email Notification Placeholder

Email notifications are future scope. SMTP settings may exist as placeholders, but email delivery is not implemented as a current feature.

Possible future email uses:

- Invite delivery after an approved invite workflow is implemented.
- Verification request status updates.
- Admin notice for pending verification requests.
- Admin notice for failed backups or service health checks.
- Account recovery after a reviewed recovery design exists.
- Meeting reminders without token bodies.

Email rules before implementation:

- Do not add an external provider in this stage.
- Do not send raw invite tokens unless the invite delivery workflow explicitly approves it.
- Do not send recovery tokens until account recovery is implemented and reviewed.
- Do not send Jitsi JWT bodies.
- Do not send passwords or session values.
- Avoid message previews and sensitive room names by default.
- Keep SMTP credentials outside Git.
- Let users opt out of non-critical email.

Email must be a delivery channel only. It must not become public registration, identity proof, verification authority, or chat authority.

## 5. Push Notification Placeholder

Push notifications are future scope and require separate privacy review.

Possible future push paths:

- Browser notifications from Converse.js.
- Native XMPP client push where supported.
- Mobile operating system push through a future reviewed service.
- Portal alerts for admin workflows after login and session policy are stable.

Push rules before implementation:

- Do not add push services in this stage.
- Do not add mobile push providers.
- Do not send message bodies by default.
- Do not send private room names for sensitive rooms unless local policy approves it.
- Do not expose verification notes, invite tokens, recovery tokens, JWT bodies, or session data.
- Keep notification subscriptions tied to approved accounts.
- Remove push access when an account is suspended or disabled.

Push notification design must account for metadata exposure to browser vendors, mobile platforms, push gateways, and device lock screens.

## 6. XMPP Native Notification Behaviour

XMPP clients handle much of the current message notification behavior.

Current model:

- Converse.js can show browser or in-page notifications depending on browser and client settings.
- Native XMPP clients may show direct message, mention, room activity, and offline message notifications.
- Prosody handles XMPP delivery and storage behavior based on enabled modules and room settings.

Rules:

- XMPP notifications must require approved XMPP accounts.
- Public XMPP registration remains disabled.
- Open federation remains disabled.
- Suspended and disabled users must lose XMPP access when provisioning sync supports it.
- Room notifications must follow room access policy.
- Native clients must not be trusted to display portal verification labels consistently.
- Users should be told that device notification behavior depends on their client and device settings.

Client-side notifications do not replace portal audit events or admin review queues.

## 7. Offline Message Handling

Offline message handling depends on Prosody configuration, XMPP client behavior, and room archive policy.

Policy:

- Direct messages may be delivered when the recipient reconnects if Prosody and the client support offline delivery.
- Room history may be available only where room settings and retention policy allow it.
- Sensitive rooms should have conservative history and preview settings.
- Message archive settings must be reviewed before broad production use.
- Offline delivery must not deliver messages to suspended or disabled users after their access is removed.
- Users without room access must not receive stored room messages.

Offline storage can expose metadata and message content depending on configuration. Operators should review room history, message archive, backups, and client behavior before relying on offline delivery for sensitive rooms.

## 8. Rate Limiting and Batching

Notifications should not create noise, spam, or denial-of-service risk.

Rate limiting targets:

- Login or session alerts.
- Invite redemption failures.
- Verification request creation.
- Admin alert generation.
- Meeting token issuance alerts.
- Future email delivery.
- Future push delivery.

Batching guidance:

- Batch non-urgent room activity.
- Batch repeated service alerts.
- Batch repeated invite failures by invite or route where possible.
- Keep urgent security alerts separate from ordinary activity.
- Avoid sending repeated notifications for the same unresolved issue.
- Let admins review queues in the portal instead of relying on constant external alerts.

Rate limit responses and alert logs must not reveal whether an account, invite, recovery token, room, or meeting exists.

## 9. User Notification Preferences

Users should control non-critical notifications when the portal supports preferences.

Suggested preference categories:

- Direct messages.
- Mentions.
- Room activity.
- Meeting reminders.
- Verification status updates.
- Account status updates.
- Email notifications when email exists.
- Push notifications when push exists.

Preference rules:

- Security-critical account and admin notices may be mandatory.
- Users should be able to quiet high-volume rooms.
- Sensitive room notifications should default to minimal previews.
- Suspended or disabled users should not receive private notifications.
- Admin preferences must not hide required trust and safety review queues.
- Preferences must not override access policy.

Preferences are future portal state and should not be treated as implemented until a later pass adds them.

## 10. Privacy Considerations

Notifications can leak sensitive data even when message content is not included.

Sensitive notification data includes:

- Usernames.
- Display names.
- Room names.
- Group or parish membership.
- Verification status.
- Meeting names.
- Invite timing.
- Admin action timing.
- IP addresses or device metadata in logs.
- Message snippets.

Privacy rules:

- Use minimal notification content.
- Avoid message previews by default in sensitive contexts.
- Avoid private room names in email or push.
- Avoid verification notes in notifications.
- Avoid raw tokens in notifications.
- Avoid logging notification payloads.
- Keep notification logs short-lived unless needed for incident review.
- Treat notification preferences and delivery metadata as user data.
- Review notification behavior before enabling federation, Tor access, bridges, library access, or mobile push.

Operators should assume device lock screens, email inboxes, browser notifications, and external push gateways may be visible outside the trusted Orthodox Connect service.

## 11. Abuse and Spam Considerations

Notification abuse can pressure users and administrators even when account access is restricted.

Risks:

- Repeated direct messages.
- Excessive mentions.
- High-volume room activity.
- Invite redemption spam.
- Verification request spam.
- Meeting reminder spam.
- Admin alert fatigue.
- Impersonation through display names in notifications.
- Bridged or federated messages triggering unexpected notifications later.

Controls:

- Keep registration invite-only.
- Keep public XMPP registration disabled.
- Keep open federation disabled.
- Rate limit invite redemption and account workflows when implemented.
- Let users mute non-critical room activity.
- Let admins revoke invites and suspend abusive accounts.
- Avoid showing verified labels unless they come from portal data.
- Keep admin alerts grouped and actionable.
- Record trust and access changes in audit events.

Automated notification suppression should not hide critical security, suspension, backup, or service-failure alerts from authorized administrators.

## 12. Failure Scenarios

Notification failures should not block core access unless the failed notification is part of a security-critical workflow.

| Failure Scenario          | Expected Behaviour |
| ------------------------- | ------------------ |
| Converse.js notification unavailable | Chat remains usable in the browser if the XMPP session works. |
| Browser notification blocked | User still sees activity inside the chat UI. |
| Native client push unavailable | User receives messages when the client reconnects if XMPP storage allows it. |
| Email delivery unavailable | Portal workflows continue, but admins rely on in-app queues or manual contact. |
| Push provider unavailable in future | Disable push and keep portal and XMPP delivery active. |
| Duplicate notifications | Suppress repeated events and preserve source records. |
| Missing admin alert | Admin review queues and audit events remain authoritative. |
| Notification contains sensitive data | Disable the channel, preserve evidence, rotate secrets if exposed, and review payloads. |
| Suspended user receives notification | Disable delivery path, remove access, and review provisioning or session state. |
| Notification storm | Rate limit, batch, or disable the noisy source while preserving critical alerts. |

Failure handling rules:

- Fail closed for access decisions.
- Do not retry raw token delivery through unsafe channels.
- Do not expose internal hostnames or stack traces in notification errors.
- Preserve audit events and source records.
- Notify users only after administrator review when privacy or account safety is affected.

## 13. Rollback Plan

Notification rollback should remove or reduce delivery without deleting source records.

Rollback steps:

1. Disable the faulty notification channel or delivery rule.
2. Confirm portal, Prosody, Converse.js, Jitsi, backups, and reverse proxy still work.
3. Confirm public registration remains disabled.
4. Confirm open federation remains disabled.
5. Confirm Jitsi authentication remains enabled.
6. Confirm admin routes remain role-gated.
7. Confirm suspended and disabled users cannot receive private access.
8. Preserve audit events, notification logs, and operator notes for review.
9. Remove or redact unsafe notification templates if they exposed private data.
10. Rotate secrets if tokens, credentials, JWTs, sessions, or `.env` values were exposed.
11. Restore the previous notification policy.
12. Record the rollback result in operator notes or portal audit records where supported.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
