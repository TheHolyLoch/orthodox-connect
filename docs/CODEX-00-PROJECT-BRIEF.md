# Orthodox Connect Project Brief

## Project Purpose

Orthodox Connect is a lightweight secure F/OSS communications platform for Orthodox parishes, clergy, monastics, and laity.

The project exists to provide parish and community communication tools that can be self-hosted, audited, and operated without dependence on commercial social platforms. The intended system should support trusted invitations, parish-level moderation, role-aware access, group chat, direct messaging, and authenticated video rooms.

The preferred direction is to build around mature open protocols and existing F/OSS services where possible, with only a small custom application layer for workflows that are specific to Orthodox parish use.

## Non-Goals

- Replacing every existing parish website, mailing list, phone tree, or bulletin workflow.
- Building a general public social network.
- Building a centralized commercial SaaS platform as the only deployment model.
- Treating IRC as the primary trust, identity, or access-control layer.
- Creating a custom chat protocol when XMPP can meet the need.
- Creating a custom video conferencing stack when Jitsi Meet can meet the need.
- Automating spiritual, pastoral, disciplinary, or clergy verification decisions.
- Making final technology choices before the open questions are resolved.

## Target Users

- Parish clergy who need trusted communication spaces for parish life.
- Monastics who need low-friction private communication with controlled access.
- Parish administrators who manage invitations, verification, roles, and room access.
- Laity who need beginner-friendly chat, announcements, and video room access.
- Technical maintainers who deploy and operate the stack for a parish, diocese, monastery, or trusted community.

## MVP Scope

- Docker Compose deployment for a single Orthodox Connect instance.
- Prosody XMPP as the lightweight chat and identity-adjacent messaging core.
- Web-based XMPP chat through Converse.js or another beginner-friendly web XMPP client.
- Authenticated user accounts with invitation-based onboarding.
- Manual verification workflows for trusted access.
- Basic roles such as administrator, clergy, monastic, member, and guest, subject to later refinement.
- Controlled group rooms for parish, clergy, catechumen, youth, ministry, or private community use.
- Direct messaging where permitted by site policy.
- Jitsi Meet integration for authenticated video rooms.
- A small custom admin portal for invitations, manual verification, roles, and room access.
- Basic operational documentation for self-hosted deployment.

## MVP Status

Implemented in the current repository:

- Docker Compose stack with Caddy, PostgreSQL, Prosody, Converse.js, Jitsi Meet, and a portal placeholder service.
- Caddy routing for portal, chat, Jitsi, XMPP browser transports, and a disabled library placeholder.
- Prosody configuration with public registration disabled and federation disabled.
- Converse.js static frontend configured through environment variables.
- Portal migrations and CLI workflows for invites, verification, room access, meeting tokens, and audit events.
- Minimal portal admin UI for viewing users, groups, roles, invites, verification requests, rooms, and audit events.
- Local backup, restore, and backup listing scripts.

Current limits:

- The portal is not packaged as a production web image yet.
- The portal CLI and admin UI run from the repository with a Python virtual environment.
- No public signup flow exists.
- Prosody account provisioning is not automated by the portal yet.
- Library and Tor access are placeholders for later work.
- SMTP settings are placeholders and email delivery is not implemented.

## Future Scope

- Kavita or similar service for PDF and ebook library access.
- Tor onion services for censorship-resistant access.
- IRC bridge or fallback access where useful, without making IRC the primary trust layer.
- Federation policy controls for XMPP, if federation is enabled.
- Mobile client guidance for XMPP-compatible apps.
- Parish directory features, if privacy and consent requirements are resolved.
- Event announcements or bulletin-style broadcast features.
- Moderation tooling for room owners and administrators.
- Remote backup providers.
- Multi-parish or diocese-level deployment models.

## Security Assumptions

- The platform is intended for private community communication, not anonymous public registration.
- Trust starts with invitation, manual verification, and local administrator judgment.
- Administrators are trusted operators and may have access to server-side metadata.
- The platform should minimize sensitive data collection.
- Secrets must live outside version control.
- Transport security is required for browser and client access.
- Role and room access controls must be explicit and auditable.
- Video rooms should require authentication or controlled access.
- Public federation, if enabled, changes the threat model and must be decided intentionally.
- End-to-end encryption support depends on the selected XMPP clients and server modules.

## Deployment Assumptions

- The primary deployment target is a small VPS, parish server, or trusted hosted environment.
- Docker Compose is the preferred deployment method.
- The initial deployment model is a single-instance stack.
- The operator controls DNS, TLS certificates, backups, and firewall policy.
- Services may include Prosody, a web XMPP client, Jitsi Meet, the custom admin portal, and supporting storage.
- Caddy is the reverse proxy.
- Email or another out-of-band channel is still needed for invitation delivery and account recovery.
- Tor onion access is future scope, not required for the MVP.

## Components Under Consideration

- Prosody XMPP for chat, account-adjacent messaging, rooms, and XMPP server functions.
- Converse.js as the preferred candidate for a beginner-friendly web XMPP interface.
- Other web XMPP clients if Converse.js does not meet usability or integration needs.
- Jitsi Meet for authenticated video rooms.
- A small custom admin portal for invitations, manual verification, roles, and room access.
- Kavita or a similar F/OSS library service for later PDF and ebook access.
- Docker Compose for deployment and service orchestration.
- Tor onion services for later censorship-resistant access.
- IRC bridge or fallback only where useful, not as the primary trust layer.

## Open Questions

- How should Prosody account provisioning be connected to portal-approved users?
- What production packaging should be used for the portal service?
- What email or out-of-band channel should deliver invitations?
- What minimum server resources should be recommended after real Jitsi load testing?
- Which library service, if any, should be selected after the MVP?
