# Orthodox Connect Architecture

## Component Diagram

```text
                         Internet
                            |
                            v
                    +---------------+
                    | Reverse Proxy |
                    +---------------+
                      |      |     |
          HTTPS/WSS  |      |     | HTTPS
                      |      |     |
                      v      |     v
        +----------------+   |   +------------+
        | Converse.js    |   |   | Jitsi Meet |
        | Web Frontend   |   |   +------------+
        +----------------+   |       |
                 |           |       |
                 | BOSH/WSS  |       | Auth policy
                 v           v       v
              +---------------------------+
              |         Prosody           |
              | XMPP, MUC, auth-adjacent  |
              +---------------------------+
                           ^
                           |
                           | Account, role, room policy
                           |
                  +----------------+
                  | Portal         |
                  | Admin workflow |
                  +----------------+
                           |
                           v
                  +----------------+
                  | PostgreSQL     |
                  | Portal state   |
                  +----------------+

Later phase:

        +--------+       +---------+
        | Kavita |       | Tor     |
        | Library|       | Onion   |
        +--------+       +---------+
```

## Service List

| Service              | MVP Status | Purpose                                                                                                    |
| -------------------- | ---------- | ---------------------------------------------------------------------------------------------------------- |
| Reverse proxy        | Required   | Public HTTPS entrypoint, TLS termination, routing to internal services.                                     |
| Portal               | Required   | Invitations, manual verification, role assignment, room access policy.                                      |
| PostgreSQL           | Required   | Stores portal users, invitations, verification records, roles, and policy.                                  |
| Prosody              | Required   | XMPP server for accounts, messaging, multi-user chat, and access control.                                   |
| Converse.js frontend | Required   | Browser chat interface backed by Prosody.                                                                  |
| Jitsi Meet           | Required   | Authenticated video meetings tied to approved users or controlled rooms.                                    |
| Redis                | Optional   | Only justified if the portal needs sessions, queues, rate limits, or locks that do not fit PostgreSQL well. |
| Kavita               | Later      | PDF and ebook library access after core communication features are stable.                                  |
| Tor                  | Later      | Onion access after the normal HTTPS deployment is stable.                                                   |

Current service names in Compose:

| Compose Service | Public Ports        | Notes                                                  |
| --------------- | ------------------- | ------------------------------------------------------ |
| `reverse-proxy` | `80/tcp`, `443/tcp` | Caddy public entrypoint and ACME client.               |
| `portal`        | None                | Placeholder container. Portal tools run from the repo. |
| `postgres`      | None                | Portal PostgreSQL database.                            |
| `prosody`       | None                | Internal XMPP service reached through Caddy.           |
| `converse`      | None                | Static Converse.js frontend behind Caddy.              |
| `jitsi-web`     | None                | Jitsi web service behind Caddy.                        |
| `jitsi-prosody` | None                | Internal Jitsi XMPP service.                           |
| `jitsi-jicofo`  | None                | Internal Jitsi focus service.                          |
| `jitsi-jvb`     | `10000/udp`         | Jitsi media transport.                                 |

## Data Flows

### Browser Chat Flow

1. A user opens the Orthodox Connect web URL.
2. The reverse proxy serves the Converse.js frontend.
3. Converse.js connects to Prosody over a browser-safe XMPP transport such as WebSocket or BOSH.
4. Prosody authenticates the XMPP account and applies room access rules.
5. Messages move through Prosody for direct chat and multi-user chat rooms.

### Portal Admin Flow

1. An administrator signs in to the portal.
2. The portal reads and writes portal state in PostgreSQL.
3. The administrator creates invitations, reviews verification status, assigns roles, and grants room access.
4. The portal records access decisions and audit events in PostgreSQL.
5. Prosody account provisioning and direct room synchronization are still future integration work.

### Video Flow

1. A verified user requests or joins a meeting link.
2. The reverse proxy routes the request to Jitsi Meet.
3. The portal issues JWT tokens for approved users or explicitly allowed guests.
4. Jitsi accepts only valid JWT-authenticated access.
5. Chat remains in XMPP rooms unless a meeting-specific Jitsi chat policy is selected later.

## Account Lifecycle

1. Invitation created by an administrator.
2. Invite delivered through an approved out-of-band method.
3. User accepts the invitation and creates account credentials.
4. Account starts in a pending state.
5. Administrator manually verifies the user.
6. Administrator assigns parish or group membership, roles, and room access.
7. User gains portal-modeled room and meeting access based on policy.
8. Administrator can suspend, disable, or remove access.
9. Prosody account provisioning remains future work.

## Room and Channel Model

The MVP should use Prosody multi-user chat rooms as the primary group communication model.

Room types under consideration:

- Parish-wide room for general parish communication.
- Clergy room for clergy-only communication.
- Monastic room for monastic-only communication.
- Ministry rooms for choir, catechism, youth, outreach, or similar groups.
- Private rooms for limited-access pastoral or administrative needs.
- Announcement room where only approved roles can post.

Room access is modeled in the portal. Prosody MUC access synchronization remains future work.

## Parish and Group Model

A parish or community is the main administrative boundary.

Each parish or community may have:

- A display name.
- Administrators.
- Verified members.
- Role assignments.
- Default rooms.
- Optional ministry or private groups.
- Access policy for shared rooms and video meetings.

The MVP assumes a single Orthodox Connect instance can host one parish or a small set of related groups. Multi-parish governance is a future design area unless needed for the first deployment.

## Shared Inter-Group Channel Model

Shared channels allow controlled communication between groups without merging their full membership or administrative authority.

Examples:

- Shared clergy channel across trusted parishes.
- Shared catechumen channel across a mission and its parent parish.
- Shared announcement room for a deanery or monastery-affiliated community.

MVP behavior should be conservative:

- Shared channels must be created by administrators.
- Each participating group must approve its own members.
- Room membership must be explicit.
- Shared channel administrators must be named.
- Shared channels must not imply full access to either group.

## Admin and Verification Workflow

The portal is the control plane for human trust decisions.

Workflow:

1. Administrator creates an invitation.
2. User accepts and creates an account.
3. User appears in the portal as pending verification.
4. Administrator reviews the user through local parish knowledge or another approved method.
5. Administrator records the verification state with minimal necessary notes.
6. Administrator assigns roles and room access.
7. Portal applies or queues the required Prosody policy changes.
8. Administrator can audit active users, roles, invitations, and room memberships.

The system must not automate clergy status, monastic status, parish standing, or pastoral trust decisions.

## Video Meeting Flow

Jitsi Meet provides video rooms.

Preferred MVP flow:

1. User signs in to Orthodox Connect.
2. User opens a video room from the portal, chat frontend, or a controlled meeting link.
3. Jitsi requires authentication or a validated room access decision.
4. Room creation may be restricted to approved roles.
5. Joining may be restricted to approved users, room members, or invited guests.
6. Meeting names should not grant access by themselves.

The current Jitsi integration uses JWT tokens issued by portal commands.

## Library Integration Placeholder

Kavita or a similar F/OSS service may provide PDF and ebook library access in a later phase.

The library should not be part of MVP unless communication features are already stable. Future integration should consider:

- Role-based access to collections.
- Separate library permissions from chat permissions.
- Copyright and distribution policy.
- Storage size, backups, and import workflows.
- Whether the portal should provision library users.

## Federation Policy

MVP federation should be disabled by default unless a specific deployment requires it.

Reasons:

- Private parish communication has a smaller trust boundary.
- Manual verification is easier to reason about inside one instance.
- Public federation changes spam, abuse, privacy, moderation, and support requirements.

Federation may be reconsidered later with explicit policy controls:

- Allowed domains.
- Blocked domains.
- Room-level federation rules.
- Administrator approval for external contacts.
- Clear user-facing labels for external accounts.

## Tor and Onion Access Placeholder

Tor onion access is a later-phase feature.

Expected future model:

- Keep the normal HTTPS deployment as the primary path.
- Add onion access for portal and chat after the core stack is stable.
- Decide whether Jitsi over onion is practical before promising support.
- Document operational risks, abuse handling, and account recovery limits.

Tor support must not weaken normal authentication, authorization, or audit controls.

## Out of Scope for MVP

- Custom chat protocol design.
- Public social network features.
- Open public registration.
- Automated clergy, monastic, or parish membership verification.
- Full multi-parish governance.
- Public XMPP federation by default.
- IRC as a primary identity or trust layer.
- Kavita or library access as a required MVP service.
- Tor onion access as a required MVP service.
- Mobile app development.
- End-to-end encrypted group chat guarantees before client and server support are verified.
- Payment processing, donations, fundraising, or parish accounting.
- Replacement of parish websites or parish management systems.
