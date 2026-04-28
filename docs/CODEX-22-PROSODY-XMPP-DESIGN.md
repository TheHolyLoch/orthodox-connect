# Orthodox Connect Prosody and XMPP Design

## 1. XMPP Goals

XMPP is the primary chat protocol for Orthodox Connect.

Goals:

- Provide direct messaging and group chat through a mature open protocol.
- Use Prosody as a small, auditable XMPP server.
- Keep public registration disabled.
- Keep open federation disabled unless trusted federation is approved later.
- Route browser chat through HTTPS WebSocket or BOSH for Converse.js.
- Keep account access tied to portal invitation, approval, suspension, role, and room policy.
- Support multi-user chat rooms for parish, group, clergy, monastic, admin, and invite-only spaces.
- Avoid claiming platform-wide end-to-end encryption unless the selected clients and workflow prove it for that case.
- Keep internal XMPP service ports private unless a reviewed deployment requires native client access.

The MVP should keep XMPP simple and closed while the portal trust model matures.

## 2. Prosody Role in the Platform

Prosody is the chat service. It handles XMPP sessions, browser XMPP transports, roster-related features, presence, and multi-user chat.

Prosody responsibilities:

- Host the Orthodox Connect XMPP domain.
- Host the MUC component for rooms and channels.
- Authenticate XMPP users after accounts exist.
- Serve browser-safe XMPP transports behind the reverse proxy.
- Store XMPP runtime data in the Prosody data volume.
- Keep public registration disabled.
- Keep server-to-server federation disabled for MVP.

Portal responsibilities remain separate:

- Invite creation and redemption.
- Manual verification.
- Role assignment.
- Group membership.
- Room policy and membership decisions.
- Meeting policy and token issuance.
- Audit events.

Current limit:

- The portal does not yet provision Prosody accounts or synchronize room policy directly into Prosody.

## 3. XMPP Domain Model

XMPP hostnames are configured through environment variables.

| Variable                    | Purpose |
| --------------------------- | ------- |
| `XMPP_DOMAIN`               | Main user XMPP domain. |
| `XMPP_ADMIN_JID`            | Prosody admin JID. |
| `XMPP_MUC_DOMAIN`           | MUC room component domain. |
| `XMPP_UPLOAD_DOMAIN`        | Reserved upload component domain for later review. |
| `XMPP_REGISTRATION_ENABLED` | Must remain `false` for MVP. |

Current model:

- Users should eventually receive JIDs under `XMPP_DOMAIN`.
- Group chat rooms should live under `XMPP_MUC_DOMAIN`.
- Browser clients reach Prosody through the chat hostname and reverse proxy routes.
- Native XMPP client ports are not published in the current Compose model.
- Jitsi uses its own internal XMPP service and domains, separate from the main Prosody service.

Domain rules:

- Do not hard-code real production domains in repository files.
- Do not use `XMPP_DOMAIN` for Jitsi internal domains.
- Do not publish federation DNS records until trusted federation is approved.
- Do not expose Prosody admin or internal service endpoints publicly.

## 4. Account Provisioning Model

Account provisioning is planned but not implemented.

Target model:

1. Administrator creates an invite in the portal.
2. User redeems the invite and creates a portal account.
3. User remains pending until approved where policy requires it.
4. Administrator approves the user and assigns group membership or roles.
5. Portal creates or enables the matching Prosody account.
6. Portal records the XMPP JID in `users.xmpp_jid`.
7. Portal applies or queues room access changes for approved rooms.
8. Suspended or disabled users lose Prosody access.

Provisioning rules:

- Public self-registration must remain disabled.
- Users must not create Prosody accounts directly.
- Users must not self-assign privileged roles through XMPP.
- Account creation must be auditable through portal events.
- Suspensions must block XMPP login and room access.
- Account recovery must not bypass portal approval or suspension.

Implementation options for later review:

| Option                         | Notes |
| ------------------------------ | ----- |
| Prosody admin command wrapper  | Simple, but must avoid shell injection and secret leakage. |
| Prosody module or HTTP API     | Cleaner integration, but requires implementation and security review. |
| External auth tied to portal   | Centralizes identity, but increases coupling and availability risk. |
| Manual operator provisioning   | Acceptable only as temporary MVP operation for small deployments. |

No provisioning implementation is added by this document.

## 5. Registration Policy

Registration policy is closed by default.

Required policy:

- `XMPP_REGISTRATION_ENABLED=false`.
- `allow_registration=false`.
- `mod_register` disabled.
- No public signup endpoint in Prosody.
- No direct account creation by ordinary users.
- No federation-based registration.

The current Prosody config fails startup if `XMPP_REGISTRATION_ENABLED` is not `false`.

Only reviewed administrator workflows may create users. Reusable invites must remain explicit, expiring, and audited by the portal.

## 6. Authentication Model

Current Prosody authentication:

- `authentication = 'internal_hashed'`.
- Password material is stored in Prosody data, not in Git.
- Browser login reaches Prosody through Converse.js over WebSocket or BOSH.

Target authentication direction:

- Portal remains the source of account approval and suspension state.
- Prosody account credentials should be created only after portal approval policy allows it.
- Future external authentication may be reviewed only after portal login and account recovery are stable.
- Admin and privileged users should have stricter recovery and suspension review.

Authentication rules:

- Do not log passwords.
- Do not expose Prosody credential files.
- Do not publish native client ports until client support and security policy are reviewed.
- Do not let XMPP authentication grant portal admin rights.
- Do not let a valid XMPP login override portal suspension state.

## 7. MUC and Channel Model

Prosody MUC is the group chat foundation.

MUC responsibilities:

- Host parish and group rooms.
- Support room membership and moderator state where configured.
- Support room history only where retention policy allows it.
- Keep room creation restricted.
- Keep sensitive rooms hidden from users without access where possible.

Portal room scopes:

| Portal Scope        | Intended XMPP Meaning |
| ------------------- | --------------------- |
| `public_to_members` | Visible and joinable for approved members. |
| `group_only`        | Available only to active members of the owning group. |
| `clergy_only`       | Available only to users with approved clergy verification and explicit policy access. |
| `monastic_only`     | Available only to users with approved monastic verification and explicit policy access. |
| `admin_only`        | Available only to approved administrator roles. |
| `invite_only`       | Available only to named users or explicit room members. |

Current Prosody config:

- Defines the MUC component from `XMPP_MUC_DOMAIN`.
- Restricts room creation to admins.
- Enables MUC message archive support through `muc_mam`.

Policy:

- Portal room policy is the source of truth.
- Prosody MUC state should be synchronized from portal policy in a later implementation pass.
- Suspended users must be removed or blocked from rooms.
- Shared inter-group rooms must use explicit membership.
- Room creation must remain restricted to approved roles.

## 8. Room Privacy Levels

Room privacy must match the portal access model.

Privacy levels:

| Level               | Access Model |
| ------------------- | ------------ |
| `public_to_members` | Approved local members can see and join. |
| `group_only`        | Active members of a specific group can see and join. |
| `clergy_only`       | Approved clergy users can see and join where scoped. |
| `monastic_only`     | Approved monastic users can see and join where scoped. |
| `admin_only`        | Approved administrators can see and join where scoped. |
| `invite_only`       | Explicit room membership is required. |

Rules:

- Private room names should not be visible to users without access.
- Clergy, monastic, admin, youth, and pastoral room names require careful exposure rules.
- Room membership lists can reveal sensitive information and should be restricted.
- Message history settings must be reviewed per room type.
- Announcement rooms should separate read access from posting rights where supported.
- Federated or external users must be clearly marked if trusted federation is later enabled.

## 9. WebSocket and BOSH Access for Converse.js

Converse.js connects to Prosody through browser-safe transports behind Caddy.

Current browser transport routes:

| Public Path       | Backend          | Purpose |
| ----------------- | ---------------- | ------- |
| `/xmpp-websocket` | `prosody:5280`   | XMPP WebSocket for browser clients. |
| `/http-bind`      | `prosody:5280`   | BOSH fallback for browser clients. |

Current environment variables:

| Variable                 | Purpose |
| ------------------------ | ------- |
| `CONVERSE_WEBSOCKET_URL` | WebSocket URL used by the chat frontend. |
| `CONVERSE_BOSH_URL`      | BOSH URL used by the chat frontend. |

Rules:

- Browser XMPP traffic should use HTTPS or WSS through the reverse proxy.
- WebSocket upgrades must be preserved by Caddy.
- Prosody `5280/tcp` should remain internal.
- Native XMPP client ports should remain closed until a reviewed client support policy exists.
- Query strings and tokens must not be logged unnecessarily by the reverse proxy.

## 10. OMEMO Expectations and Limitations

OMEMO is a client-side encryption feature. It is not a platform-wide guarantee.

Expectations:

- OMEMO behavior depends on the selected client, device state, room type, and user behavior.
- Browser chat may not offer the same OMEMO behavior as native XMPP clients.
- Native Android and iOS clients must be tested before recommendation.
- Device verification can confuse non-technical users and needs support guidance.

Limitations:

- Prosody can still see metadata such as account identifiers, room names, presence, timestamps, IP addresses, and room membership.
- Message archives may store message content if enabled and not end-to-end encrypted.
- External clients may not show portal verification labels consistently.
- Screenshots of OMEMO state must not be treated as clergy, monastic, or admin verification.

Policy:

- Do not claim all chat is end-to-end encrypted.
- Review one-to-one chat and group chat separately.
- Review sensitive rooms before recommending native clients or OMEMO-dependent workflows.
- Keep portal verification as the source of truth for roles and identity labels.

## 11. File Upload Policy

File upload is not enabled as a current MVP feature.

Current status:

- `XMPP_UPLOAD_DOMAIN` is reserved in environment configuration.
- No upload component should be treated as implemented until reviewed and configured.

Future file upload requirements:

- Upload access must require approved accounts.
- Upload access must respect room, group, and role policy where practical.
- Suspended users must lose upload access.
- Upload size limits must be defined.
- Retention and deletion policy must be defined.
- Malware and abuse handling must be reviewed.
- Copyright and sensitive-document risks must be reviewed.
- Upload storage must be included in backups only after policy approval.

Rules:

- Do not allow anonymous public upload.
- Do not expose upload directories through the reverse proxy as static public files.
- Do not use chat uploads as the library service.
- Do not commit uploaded files, thumbnails, or generated metadata to Git.

## 12. Federation Policy

Open federation is disabled for MVP.

Current policy:

- Prosody disables `s2s`.
- XMPP federation ports are not published.
- No trusted partner servers are configured.
- No remote domains are allowlisted.

Reasons:

- Local invite-only trust is easier to audit.
- Clergy and monastic verification does not transfer automatically.
- Federation increases spam, impersonation, moderation, metadata, and support risk.
- Room names, membership, presence, and message history can reveal sensitive community details.

Future trusted federation requirements:

- Approve each trusted server individually.
- Record server identity, admin contacts, and scopes.
- Allow only named scopes such as admin contact or specific shared rooms.
- Audit approval, scope changes, and revocation.
- Remove remote users from shared rooms on revocation.
- Test federation with non-sensitive rooms first.

Federation must not be enabled by this document.

## 13. Admin JID Policy

Prosody admin JIDs are configured with `XMPP_ADMIN_JID`.

Policy:

- Admin JIDs must belong to trusted operators only.
- Admin JIDs must not be shared accounts where avoidable.
- Admin JIDs must not be ordinary user accounts unless the operator accepts the risk.
- Prosody admin interfaces must not be exposed publicly.
- Admin JID changes should be recorded in operator notes or portal audit records where supported.
- Admin credentials must not be committed to Git.
- Recovery of admin JIDs must require operator review.

Current config includes `admin_adhoc`. This must remain reachable only to authenticated admins and must not be exposed as a public administrative endpoint.

## 14. Logging Policy

Prosody logging should support operations and incident response without collecting message content.

Log intentionally:

- Service start and stop events.
- Configuration errors.
- Authentication failures.
- Connection failures.
- Browser transport errors.
- MUC creation and access-control errors where available.
- Federation attempts if federation is later enabled.

Avoid logging:

- Passwords.
- Invite tokens.
- Recovery tokens.
- Session cookies.
- Message bodies.
- Private room contents.
- Full request bodies.
- `.env` contents.
- TLS private keys or Prosody private data.

Policy:

- Keep debug logging off by default in production.
- Keep retention short unless there is a documented operational reason.
- Treat Prosody logs as sensitive metadata.
- Do not commit logs to Git.
- Do not include logs in public support requests without review.

## 15. Backup Requirements

Prosody backups are required because Prosody stores XMPP runtime state.

Back up:

- Prosody data volume.
- Prosody configuration under `prosody/`.
- Relevant environment values from operator-controlled configuration storage.
- MUC room state where stored by Prosody.
- Message archive data if enabled.
- Upload data if upload support is enabled later.

Do not back up to Git:

- Prosody data directories.
- User credentials.
- Private keys.
- Message archives from real rooms.
- Uploads.
- Logs.

Restore requirements:

- Restore PostgreSQL portal state first.
- Restore Prosody configuration and data.
- Confirm `XMPP_REGISTRATION_ENABLED=false`.
- Confirm federation remains disabled unless explicitly approved later.
- Confirm browser WebSocket or BOSH routes work through Caddy.
- Review room access and suspended users before reopening chat to users.

If Prosody data cannot be restored, rebuild rooms from portal policy where possible and document any lost message history.

## 16. Rollback Plan

Prosody rollback must preserve portal trust state and avoid opening chat access too broadly.

Rollback steps:

1. Stop public chat routes if the current Prosody state is unsafe.
2. Preserve current Prosody data and logs for review.
3. Restore the last known-good Prosody config or data backup.
4. Confirm `XMPP_REGISTRATION_ENABLED=false`.
5. Confirm `allow_registration=false`.
6. Confirm `s2s` remains disabled.
7. Confirm Prosody browser transports work only through the reverse proxy.
8. Confirm portal users, roles, room memberships, suspensions, and audit records remain intact.
9. Restart Prosody and chat frontend.
10. Test chat access with disposable approved and denied accounts where available.
11. Record the rollback reason and result.

Rollback must not delete portal users, roles, verification records, rooms, meetings, audit events, backups, Jitsi state, or unrelated service configuration.
