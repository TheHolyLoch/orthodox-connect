# Orthodox Connect Converse Web Chat Design

## 1. Web Chat Goals

The web chat should give approved Orthodox Connect users a simple browser path into XMPP chat.

Goals:

- Use Converse.js as the browser chat client.
- Keep public registration disabled.
- Connect to Prosody through reverse-proxied browser transports.
- Support direct messaging and group rooms where policy allows.
- Keep account access tied to portal invitation, approval, suspension, roles, group membership, and room policy.
- Avoid exposing XMPP internals, service ports, passwords, or tokens to ordinary users.
- Avoid claiming platform-wide end-to-end encryption.
- Keep the first chat experience understandable for non-technical parish, diocesan, monastic, and community users.

The web chat is an access layer for Prosody. It is not the source of truth for identity, verification, room policy, or audit records.

## 2. Converse.js Role in the Platform

Converse.js is the current web chat frontend for Orthodox Connect.

Converse.js responsibilities:

- Render the browser chat interface.
- Accept user XMPP sign-in.
- Connect to Prosody through WebSocket or BOSH.
- Display direct chats and MUC rooms available to the authenticated XMPP account.
- Use configured XMPP domain and MUC domain values.
- Keep the chat UI embedded under the Orthodox Connect chat hostname.

Portal responsibilities remain separate:

- Invite creation and redemption.
- User approval and suspension.
- Clergy, monastic, and parish admin verification.
- Role assignment.
- Group membership.
- Room policy and explicit room membership.
- Audit events.

Current frontend files:

| File                           | Purpose |
| ------------------------------ | ------- |
| `converse/index.html`          | Static chat page and Converse.js root. |
| `converse/style.css`           | Basic Orthodox Connect chat shell styling. |
| `converse/config.js.template`  | Runtime Converse.js configuration template. |

## 3. Beginner-Friendly Chat UX

The chat screen should make the main action obvious without requiring protocol knowledge.

UX rules:

- Use local language such as chat, room, direct message, account, parish, group, clergy, monastic, and administrator.
- Avoid user-facing labels such as XMPP, MUC, BOSH, WebSocket, Prosody, stanza, or federation unless needed for support.
- Keep sign-in copy short.
- Make it clear that the account comes from the community administrator.
- Show only rooms the user can access where the backend supports that policy.
- Keep restricted rooms out of broad discovery.
- Use verified role labels only when they come from portal data or a future reviewed integration.
- Make empty states useful, such as telling approved users to contact an administrator if no rooms are available.
- Keep ordinary chat screens separate from administrator workflows.

Converse.js default screens may need later UX refinement, but this document does not implement those changes.

## 4. Login and Session Model

Current Converse.js login uses XMPP credentials.

Current configuration direction:

- `authentication: 'login'`.
- `auto_login: false`.
- `locked_domain` is set from `XMPP_DOMAIN`.
- Public registration is not configured in the frontend.

Policy:

- Users should receive XMPP access only after portal policy allows it.
- Users should not create XMPP accounts directly through the chat frontend.
- Suspended or disabled users must lose XMPP access.
- Chat login must not grant portal admin rights.
- Portal login and XMPP login may remain separate until account provisioning and single sign-on are designed.
- Passwords must not be logged by Converse.js, Caddy, Prosody, or portal tooling.

Current limit:

- The portal does not yet provision Prosody accounts automatically.
- The portal does not yet provide single sign-on for Converse.js.

## 5. XMPP Connection Model

Converse.js connects to the main Orthodox Connect Prosody service.

Current configured values:

| Variable                    | Purpose |
| --------------------------- | ------- |
| `XMPP_DOMAIN`               | User XMPP domain and locked login domain. |
| `XMPP_MUC_DOMAIN`           | Group chat room component domain. |
| `CONVERSE_WEBSOCKET_URL`    | Browser WebSocket endpoint. |
| `CONVERSE_BOSH_URL`         | Browser BOSH endpoint. |

Connection rules:

- Browser chat must connect through the reverse proxy.
- Prosody internal ports must stay private.
- Native XMPP client ports remain closed until a reviewed client support policy exists.
- Federation remains disabled unless a later trusted federation policy enables it.
- Connection errors should show safe user-facing messages and avoid internal hostnames.

## 6. WebSocket and BOSH Choice

WebSocket is the preferred browser transport. BOSH remains the fallback path.

Current routes:

| Public Path       | Backend        | Use |
| ----------------- | -------------- | --- |
| `/xmpp-websocket` | `prosody:5280` | Preferred XMPP WebSocket transport. |
| `/http-bind`      | `prosody:5280` | BOSH fallback transport. |

Policy:

- Prefer `CONVERSE_WEBSOCKET_URL` for normal browser chat.
- Keep `CONVERSE_BOSH_URL` configured for compatibility.
- Preserve WebSocket upgrades in Caddy.
- Do not publish Prosody `5280/tcp` directly to the host.
- Do not log credentials, cookies, invite tokens, or sensitive query strings.

If WebSocket is unavailable, BOSH can keep basic browser chat working while the proxy or client issue is reviewed.

## 7. Room and Channel Discovery Model

Room discovery must follow portal policy.

Room scopes:

- `public_to_members`
- `group_only`
- `clergy_only`
- `monastic_only`
- `admin_only`
- `invite_only`

Rules:

- Users should see only rooms they may access.
- Restricted room names should not be exposed to unauthorized users.
- Clergy, monastic, admin, youth, private, and pastoral room names require conservative visibility.
- Shared inter-group rooms must be explicit.
- Future federated rooms must be clearly marked as remote or shared.
- Portal room policy remains the source of truth.

Current limit:

- Prosody room state is not fully synchronized from portal policy yet.
- Converse.js can show what Prosody exposes to the logged-in account, but it does not replace portal access checks.

## 8. Direct Message Policy

Direct messages are allowed only where local policy permits them.

Policy:

- Approved users may use direct messages if the deployment enables them.
- Suspended or disabled users must lose direct message access.
- Users must not use display names to impersonate clergy, monastics, parish admins, or platform admins.
- Verified status should come from the portal, not from user-editable names.
- Direct messages should not bypass moderation, suspension, or abuse reporting policies.
- Direct message history and archiving must be reviewed before production use.

Direct messages may be disabled or limited for some deployments if local administrators prefer room-based communication.

## 9. Group Chat Policy

Group chat uses Prosody MUC rooms.

Policy:

- Room creation remains restricted to approved roles or administrators.
- Room access is derived from portal roles, group membership, explicit room membership, and suspension state.
- Announcement rooms should separate read access from posting rights where supported.
- Clergy-only and monastic-only rooms require approved verification and explicit policy.
- Admin rooms require approved administrator roles.
- Invite-only rooms require explicit membership.
- Message archive settings must be reviewed per room type.

Group chat must not become public chat. Open federation and public registration remain disabled.

## 10. OMEMO UX Expectations and Limitations

OMEMO is a client-side encryption feature, not a platform-wide guarantee.

Expectations:

- Browser OMEMO behavior depends on Converse.js support, browser storage, device state, and room type.
- Native clients may behave differently from the browser client.
- Device verification can confuse non-technical users.
- Lost browser data may affect encrypted message access.

Limitations:

- Prosody can still see metadata such as account identifiers, room names, membership, presence, timestamps, and connection metadata.
- Server-side message archives may store message content if enabled and not end-to-end encrypted.
- External clients may not display portal verification labels.
- OMEMO status must not be treated as proof of clergy, monastic, or administrator verification.

Policy:

- Do not claim all chat is end-to-end encrypted.
- Review one-to-one chat and group chat separately before recommending OMEMO-dependent workflows.
- Keep portal verification as the source of truth for identity labels.

## 11. Notification Policy

Web chat notifications should be conservative.

Policy:

- Browser notifications should be opt-in.
- Notifications should not expose sensitive room names or message previews unless the deployment accepts that risk.
- Sensitive rooms should prefer minimal notification content.
- Notification behavior should be tested on desktop and mobile browsers before recommending it.
- Push notification services are not added by this design.
- Native mobile push is future scope and must be reviewed separately.

Users should be told that browser notifications depend on their browser and device settings.

## 12. Mobile Browser Support

Mobile browser chat is the first supported mobile chat path.

Requirements:

- Chat page fits narrow screens.
- Login controls remain readable and usable.
- Room list and conversation views avoid horizontal scrolling where practical.
- Touch targets are large enough for ordinary use.
- Browser transport works over HTTPS or WSS.
- Meeting links opened from chat still follow portal and Jitsi access policy.
- Mobile support guidance avoids asking users to understand XMPP setup.

Native Android and iOS XMPP clients remain planned support paths, not a replacement for browser chat until account provisioning and client testing are complete.

## 13. Theming and Branding

The chat frontend should look like part of Orthodox Connect without obscuring the Converse.js interface.

Branding rules:

- Use the Orthodox Connect name and local deployment name where appropriate.
- Keep styling restrained and readable.
- Keep layout functional before decorative.
- Avoid marketing-style screens when the user needs chat.
- Use consistent colors, typography, and spacing with the portal where practical.
- Do not use visual labels that can be confused with verified status.
- Do not hard-code real parish, diocesan, monastic, or production domain names.

The current frontend uses a simple chat shell around the embedded Converse.js root.

## 14. Accessibility Requirements

The chat frontend should remain usable with keyboard, screen readers, zoom, and common browser accessibility settings.

Requirements:

- Keep readable font sizes.
- Keep strong text contrast.
- Do not rely on color alone for state.
- Preserve logical focus order.
- Keep labels for sign-in fields where Converse.js allows it.
- Ensure status and error messages are readable.
- Avoid inaccessible icon-only actions unless Converse.js supplies accessible names.
- Keep mobile layout usable without horizontal scrolling.
- Avoid flashing or distracting motion.

Accessibility checks should be part of later UI work before broad parish use.

## 15. Reverse Proxy Requirements

Caddy is the public HTTP and HTTPS entrypoint for web chat.

Current requirements:

- Route `CHAT_DOMAIN` to the `converse` service for the static frontend.
- Route `/xmpp-websocket` and related paths to `prosody:5280`.
- Route `/http-bind` and related paths to `prosody:5280`.
- Preserve WebSocket upgrades.
- Keep Prosody internal ports private.
- Keep Converse.js internal service ports private.
- Apply chat security headers.
- Avoid logging sensitive query strings or credentials.

Current public exposure:

| Public Route      | Purpose |
| ----------------- | ------- |
| `CHAT_DOMAIN`     | Converse.js web chat frontend and browser XMPP transport paths. |

The reverse proxy should remain the only public HTTP or HTTPS entrypoint for browser chat.

## 16. Rollback Plan

Converse.js rollback should restore browser chat without weakening identity or room policy.

Rollback steps:

1. Stop or isolate the public chat route if the frontend is unsafe.
2. Preserve current Converse.js files and logs for review.
3. Restore the last known-good Converse.js static files or configuration.
4. Confirm `CONVERSE_WEBSOCKET_URL` points to the reviewed chat WebSocket route.
5. Confirm `CONVERSE_BOSH_URL` points to the reviewed BOSH route.
6. Confirm `XMPP_REGISTRATION_ENABLED=false`.
7. Confirm Prosody federation remains disabled.
8. Confirm Caddy routes chat traffic through `converse` and Prosody browser transports only.
9. Confirm internal Prosody ports are not published.
10. Test sign-in with disposable approved and denied accounts where available.
11. Confirm suspended users remain blocked at the account or Prosody policy layer.
12. Record the rollback result in operator notes or audit events where supported.

Rollback must not delete portal users, roles, groups, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
