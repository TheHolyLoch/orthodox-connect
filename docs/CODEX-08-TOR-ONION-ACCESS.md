# Orthodox Connect Tor Onion Access

## Purpose

Tor onion access is a planned censorship-resistance option for Orthodox Connect. It gives approved users another route to reach the same private community services when normal DNS, HTTPS, or network access is blocked or unsafe.

Onion access must not create a separate trust model. It must use the same invite-only registration, manual verification, role checks, audit trail, and administrator controls as the normal HTTPS deployment.

## Onion Endpoint Scope

Onion endpoints should be limited to services that work reliably in Tor Browser and do not require high-bandwidth real-time media.

Recommended onion endpoints:

| Service | Onion Endpoint | Reason |
| ------- | -------------- | ------ |
| Portal  | Yes            | Admin and user workflows should remain reachable during blocking. |
| Chat    | Yes            | Browser chat over HTTPS, WebSocket, or BOSH is the main censorship-resistant use case. |
| Library | Later          | PDF and ebook access may be useful later, but only after library access control exists. |

Services that should not have onion endpoints by default:

| Service | Onion Endpoint | Reason |
| ------- | -------------- | ------ |
| Jitsi Meet | No         | Video over Tor is likely unreliable and can create heavy load. |
| Jitsi JVB media | No     | UDP media transport does not fit normal onion service access. |
| PostgreSQL | No         | Database access must remain internal only. |
| Prosody native client ports | No | Native XMPP onion support needs a separate client and policy review. |
| Caddy admin API | No      | Internal control interfaces must stay private. |
| Docker or host admin ports | No | Host administration must not be exposed through onion services. |

## Threat Model

Onion access helps users reach the service when public routes are blocked. It does not solve endpoint compromise, account compromise, weak administrator practices, or unsafe client devices.

Primary threats:

- Discovery or leakage of private onion hostnames.
- Abuse from harder-to-identify clients.
- Increased credential stuffing or invite-token guessing through onion routes.
- Metadata exposure in application logs and backups.
- Misconfigured reverse proxy routes exposing internal services.
- Confusion between the normal public site and the onion site.
- Operators over-promising anonymity or end-to-end security.

Assumptions:

- Server operators remain trusted with server-side metadata.
- Users still authenticate with Orthodox Connect accounts.
- Admins can suspend users and revoke invites regardless of access path.
- Onion private keys are high-value secrets.

## Reverse Proxy Model

The onion route should terminate inside the existing stack and forward to the same internal services as normal HTTPS.

Model:

1. Tor onion service receives browser traffic.
2. Tor forwards traffic to an internal reverse proxy listener.
3. The reverse proxy routes onion portal traffic to `portal`.
4. The reverse proxy routes onion chat traffic to `converse` and Prosody browser transports.
5. The reverse proxy does not route onion traffic to Jitsi media, PostgreSQL, Docker, or admin control ports.

Policy:

- Onion routes must use separate hostnames from public DNS routes.
- Onion routes must import the same security headers where practical.
- Onion routes must preserve WebSocket support for chat.
- Onion routes must not bypass authentication, authorization, or audit checks.
- Onion-specific routing should be easy to disable without changing public HTTPS routing.

## Tor Container and Service Model

Tor should be added later as a dedicated service with a minimal network path.

Planned model:

- One Tor service container.
- A persistent volume or mounted secret path for onion service keys.
- Access only to the reverse proxy network path needed for portal and chat.
- No direct access from Tor to PostgreSQL, Prosody internals, Jitsi internals, or host administration.
- No public host ports required for the Tor service.
- Logs configured to avoid storing unnecessary client or circuit metadata.

The Tor service must not be added until this design is reviewed and the operator has a key backup and rotation plan.

## Onion Hostname Handling

Onion hostnames and onion private keys must be handled as operator secrets.

Rules:

- Do not commit onion hostnames before a deployment intentionally publishes them.
- Do not commit onion private keys.
- Store onion private keys in operator-controlled secret storage or protected Docker volumes.
- Back up onion private keys only if the operator wants stable onion addresses after restore.
- Rotate onion keys if private keys are exposed.
- Record where the onion hostname is published and who can distribute it.

For private communities, onion hostnames may be shared only with approved users through an approved out-of-band channel.

## Authentication Requirements

Onion access must keep the same access requirements as normal access.

Requirements:

- Public registration remains disabled.
- Invite-only onboarding remains required.
- Users must authenticate before accessing private portal or chat functions.
- Admin routes require admin roles.
- Verification decisions remain administrator-controlled.
- Suspended users remain blocked.
- Meeting token issuance remains role-gated.
- Onion access must not create anonymous read access to private rooms.

If onion access changes the risk of account recovery or invite redemption, those workflows should require stronger review before being exposed over onion.

## Rate Limiting and Abuse Controls

Tor traffic can make IP-based abuse controls weaker. Abuse controls should focus on accounts, invites, rooms, and administrator review.

Controls:

- Rate limit login attempts by account identifier and route where possible.
- Rate limit invite redemption by token and account metadata where possible.
- Keep invite tokens high entropy and expiring.
- Keep reusable invites disabled unless explicitly approved.
- Require admin review for new accounts.
- Allow administrators to suspend accounts and revoke invites quickly.
- Record onion-route use in audit metadata where useful, without storing more client data than needed.
- Keep room creation restricted to approved roles.
- Disable anonymous public meeting creation.

If abuse increases, onion access should be reduced to portal-only or disabled until reviewed.

## Tor Browser User Guidance

User guidance should be short and conservative.

Recommended guidance:

- Use Tor Browser from the official Tor Project source.
- Use the onion address exactly as provided by the community administrator.
- Do not use the onion site as proof that a message is anonymous from the server operator.
- Do not share invite links or onion addresses in public places.
- Expect video meetings to use the normal HTTPS site, not onion access.
- Report login trouble, suspicious prompts, or changed onion addresses to an administrator through an approved contact path.

Users should be told that onion access helps with reachability and network privacy, but it does not replace good account security or administrator trust.

## Operational Risks

Risks:

- Onion private key loss changes the onion address unless the key was backed up.
- Onion private key exposure allows impersonation of the onion service.
- Tor can increase login abuse and support requests.
- Users may misunderstand what Tor protects.
- Some browser features, downloads, and real-time functions may behave differently in Tor Browser.
- Operators may forget to apply the same security headers and access rules to onion routes.
- Backup archives may include onion keys if storage paths are not reviewed.

Operational requirements:

- Test onion routes with disposable data before production use.
- Keep a written key backup and rotation plan.
- Include onion service health in monitoring only after deciding what metadata may be logged.
- Review onion routing after every reverse proxy change.
- Review incident response steps before publishing an onion address.

## Rollback Plan

Rollback must be simple and must not disrupt the normal public HTTPS deployment.

Rollback steps:

1. Stop or disable the Tor service.
2. Remove onion route publication from user-facing guidance.
3. Confirm portal and chat still work over normal HTTPS.
4. Preserve audit logs and incident notes.
5. Review recent onion access for abuse or account compromise.
6. Rotate onion private keys if exposure is suspected.
7. Keep or delete onion service keys based on the incident decision.
8. Notify approved users through the normal administrator contact path.

Rollback must not remove local users, local rooms, portal audit records, normal HTTPS routes, backups, or unrelated service data.
