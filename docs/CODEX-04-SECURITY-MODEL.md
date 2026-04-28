# Orthodox Connect Security Model

## Threat Model

Orthodox Connect is intended for private community communication on a trusted self-hosted instance.

Primary threats:

- Public spam or account farming.
- Impersonation of clergy, monastics, parish admins, or parish members.
- Compromised user accounts.
- Compromised administrator accounts.
- Unauthorized room access.
- Leaked invite links.
- Misconfigured federation.
- Server compromise through exposed services or weak secrets.
- Metadata exposure through logs, backups, DNS, TLS, or server administration.
- Censorship or blocking of the public service endpoint.
- Loss of service or data through failed backups, upgrades, or operator error.

Trust assumptions:

- Platform admins and server operators are trusted with server-side metadata.
- The deployment host, database, Prosody server, Jitsi stack, and reverse proxy are part of the trusted computing base.
- Orthodox Connect should not be described as fully end-to-end secure unless the selected clients and server configuration provide that property for the specific feature.
- The MVP prioritizes controlled membership, transport security, access control, auditability, and low public attack surface.

## Current Security Controls

- Caddy is the only HTTP/HTTPS public entrypoint.
- Jitsi JVB publishes only `10000/udp` for media.
- PostgreSQL, Prosody, Converse.js, and Jitsi internal services do not publish host ports.
- Compose services use `no-new-privileges:true`.
- Prosody public registration is disabled and the config errors if `XMPP_REGISTRATION_ENABLED` is not `false`.
- Prosody federation is disabled by disabling `s2s`.
- Jitsi JWT authentication is enabled with empty JWTs rejected.
- Portal admin actions require an approved admin role in portal data.
- Invite, verification, room, and meeting actions write audit events.
- Backup scripts write local files and do not print secret values in the manifest.

## Account Security

Account creation must be invite-only. Public self-registration is out of scope for MVP.

Required account controls:

- Invitation expiration.
- Invitation revocation.
- Manual approval before normal access.
- Strong password requirements.
- Rate limiting for login and recovery attempts.
- Session expiration.
- Suspension that blocks portal, chat, room, and meeting access.
- Recovery workflow that does not bypass suspension or verification.
- Stronger recovery review for privileged roles.

Not all account controls are implemented yet. Password login, recovery, rate limiting, and MFA remain future portal work.

Privileged roles should use stricter controls:

- `parish_admin`
- `clergy_verified`
- `monastic_verified`
- `diocesan_admin`
- `platform_admin`

Multi-factor authentication is strongly preferred for administrators, but final support depends on the selected portal implementation and authentication method.

## Chat Security

Prosody is the chat core. Chat security depends on Prosody configuration, selected XMPP modules, the web client, and any external XMPP clients allowed by policy.

Baseline controls:

- Require TLS for client connections.
- Route browser XMPP traffic over HTTPS WebSocket or BOSH through the reverse proxy.
- Disable public registration.
- Limit room creation to approved roles.
- Enforce room membership and role policy.
- Disable public federation by default.
- Keep Prosody admin interfaces private.
- Avoid storing more message history than needed.

The current Prosody configuration supports browser WebSocket and BOSH through Caddy. Direct native XMPP client ports are not published.

End-to-end encryption:

- Do not claim platform-wide end-to-end encryption for MVP.
- Direct chat or group chat encryption depends on client support and user behavior.
- Server-side components may still see metadata such as account identifiers, room names, timestamps, IP addresses, roster data, and room membership.
- Message archive settings must be chosen deliberately because server-side archives change confidentiality and retention risk.

## Room Privacy Levels

Rooms should have explicit privacy levels.

| Level        | Access Model                                                            | Example Use                                  |
| ------------ | ----------------------------------------------------------------------- | -------------------------------------------- |
| public-local | Visible to approved local users, joinable by allowed local roles.        | Parish general room.                         |
| members      | Visible and joinable only by approved parish or group members.           | Ministry or catechumen room.                 |
| restricted   | Explicit room membership required.                                      | Clergy, monastic, admin, or pastoral room.   |
| announcement | Broad read access, limited post access.                                 | Parish announcements.                        |
| shared       | Explicit members from multiple approved groups.                          | Shared clergy or mission-parent parish room. |
| private      | Explicit invite-only room with named administrators and members.          | Sensitive planning or limited committee room. |

Room names, descriptions, member lists, and message history can reveal sensitive information. Restricted and private rooms should avoid exposing membership or subject matter to users without access.

## Admin Security

Administrators are high-value accounts.

Admin requirements:

- Admin actions must be audited.
- Admin privileges must be scoped.
- `platform_admin` access should be rare.
- `parish_admin` access should be limited to assigned parish or group scope.
- `diocesan_admin` access should be limited to assigned diocesan scope.
- Admins must not share accounts.
- Admin sessions should expire sooner than normal user sessions.
- Admin recovery should require manual review by another trusted admin where possible.
- Verification notes should be minimal and visible only to authorized admins.

Admin interfaces must be available only through HTTPS. Internal service admin endpoints must not be exposed publicly.

The current admin UI is minimal and role-gated, but it should be treated as early MVP tooling until the portal is packaged for production.

## Jitsi Security

Jitsi Meet should be treated as a separate real-time communication system integrated with Orthodox Connect policy.

Required controls:

- Meeting access should require authentication or validated invitation.
- Room creation should be limited to approved roles.
- Meeting names must not grant access by themselves.
- Anonymous public meeting creation should be disabled.
- Moderator privileges should be assigned intentionally.
- Sensitive meetings should use waiting room or explicit approval features if available.
- Recordings should be disabled by default.
- If recordings are enabled later, they must have explicit storage, access, retention, and consent policy.

The current stack uses JWT authentication for Jitsi. Meeting creation and token issuance are handled by portal CLI workflows.

Limitations:

- Jitsi media encryption and end-to-end behavior depends on Jitsi configuration, browser support, deployment mode, and participant clients.
- Server operators may be able to observe metadata such as meeting names, participant IP addresses, join times, and service logs.
- Jitsi over Tor is not promised for MVP and may not be practical for reliable video.

## Library Security

Kavita or a similar library service is later scope.

Future library controls:

- Separate library access policy from chat room access.
- Role-based collection access.
- No public anonymous library access unless a deployment explicitly chooses it.
- Clear copyright and distribution policy.
- Backups for library metadata and files.
- Audit access to restricted collections where practical.
- Avoid placing sensitive pastoral documents in the library unless the service and operator policy are suitable for that risk.

The MVP should not depend on library security because library access is not part of the initial required service set.

## Anti-Impersonation Controls

The system must prevent public self-asserted clergy and monastic labels.

Controls:

- Manual verification for clergy and monastic status.
- Visible verified labels only from administrator-approved records.
- No user-editable public title fields that can mimic verified status.
- Unique usernames or account identifiers.
- Display names may be user-editable only if the UI clearly separates display name from verified status.
- Audit trail for role and verification changes.
- Admin review for changes to sensitive names or labels if needed.
- Suspended or revoked users must lose verified status visibility.

Impersonation risk remains if users choose confusing display names, external clients hide verification labels, or screenshots are shared outside the platform.

## Anti-Abuse Controls

MVP anti-abuse is based on closed membership and admin control.

Controls:

- Invite-only registration.
- Manual approval.
- Room creation limits.
- Rate limiting for login, invites, recovery, and posting where supported.
- Ability to suspend accounts.
- Ability to revoke invitations.
- Ability to remove room access.
- Admin-visible audit trail.
- Federation disabled by default.
- External bridges disabled by default.
- Logs sufficient for incident response without excessive data collection.

Open federation, public bridges, reusable invites, and anonymous access all increase abuse risk and should require explicit deployment policy.

## Censorship-Resistance Plan

The primary MVP deployment is normal HTTPS over public DNS.

Later censorship-resistance plan:

- Document how to create a Tor onion endpoint for portal and chat.
- Keep onion access behind the same authentication and authorization controls.
- Treat onion service private keys as high-value secrets.
- Decide separately whether XMPP native client connections should be available over onion.
- Do not promise Jitsi over onion until tested for usability and reliability.
- Keep backups and deployment docs available to trusted operators for redeployment.

Censorship resistance does not remove the need for account security, administrator review, or careful operational security.

## Backup and Recovery

Backups protect against data loss but increase confidentiality risk.

Backup targets:

- PostgreSQL logical dumps.
- Prosody data and configuration.
- Portal configuration and uploaded files, if uploads exist.
- Jitsi configuration and generated secrets.
- Reverse proxy TLS data, if managed by the stack.
- Kavita data and library files in the later phase.
- Operator-owned `.env` and secret files through secure storage, not Git.

Recovery requirements:

- Backups should be encrypted before leaving the server.
- Backups should have access limited to trusted operators.
- Restore procedures should be tested.
- Recovery should include account and room access state, not just files.
- Old backups should be deleted per retention policy.

Backups may contain message archives, membership data, IP metadata, verification records, and admin actions. Treat them as sensitive.

## Logging Policy

Logs should support operations and incident response without becoming a parallel data store.

Log intentionally:

- Authentication success and failure metadata.
- Invitation creation, acceptance, expiration, and revocation.
- Admin actions.
- Role and verification changes.
- Suspension and restoration.
- Service errors.
- Backup and restore events.

Avoid logging:

- Passwords.
- Invite tokens.
- Recovery tokens.
- Message bodies.
- Private room contents.
- Full session cookies.
- Unneeded request bodies.

Logging limits:

- IP addresses and user agents may be useful for abuse review but are sensitive.
- Retention should be short unless a deployment has a clear reason.
- Debug logging should not be enabled in production by default.
- Logs must not be committed to Git.

## Data Minimisation

Collect the least data needed to run the community safely.

Recommended minimum data:

- Account identifier.
- Display name.
- Authentication data.
- Parish or group membership.
- Roles.
- Verification status.
- Invitation state.
- Audit events for trust and access decisions.
- Recovery metadata.

Avoid collecting by default:

- Government identity documents.
- Birth dates.
- Home addresses.
- Sensitive pastoral notes.
- Unneeded family relationships.
- Unneeded phone numbers.
- Broad profile fields.

Verification notes should be short and operational. They should record why an admin made a decision, not become a pastoral record system.

## Known Limitations

- MVP does not guarantee end-to-end encrypted communication.
- Server operators may access metadata and, depending on archive settings, message content.
- Browser-based chat depends on the security of the served frontend and user browsers.
- External XMPP clients may not display verified status consistently.
- Jitsi security depends on deployment configuration and client behavior.
- Federation is disabled by default because it changes the threat model.
- Tor access is later scope and does not solve endpoint compromise or account compromise.
- Manual verification can fail if administrators make mistakes.
- Backups and logs can leak sensitive metadata if mishandled.
- A compromised platform admin or server host can undermine the whole instance.
- The system is not a replacement for emergency communication, legal recordkeeping, pastoral case management, or diocesan canonical process.
