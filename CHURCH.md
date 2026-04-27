# Orthodox Connect for the Church

Orthodox Connect is a self-hosted communications platform for Orthodox parishes, clergy, monastics, and laity. It is built to support invite-only communities, manual verification, role-aware access, and auditable administration, without depending on commercial social platforms.

This document is written for bishops, priests, and abbots who want a clear picture of what Orthodox Connect is for and how it can serve a diocese, parish, or monastic community.

## What Problem It Solves

Most Orthodox communities rely on tools that were not designed for Church life:

- Public social platforms that reward publicity and conflict.
- Group chats that have weak access control and no durable audit trail.
- Fragmented communication across multiple apps and accounts.

Orthodox Connect aims to provide:

- A private communication home for a parish, monastery, or diocese.
- A clear, administrator-controlled membership process.
- Rooms with access based on Church roles and community membership.
- Video meetings that are not publicly creatable and can be role-gated.
- Local control of data, backups, and policy.

## What It Provides *(MVP)*

Orthodox Connect combines several proven open-source components into one system:

- Web chat in a browser.
- Group chat rooms and direct messaging through an XMPP server.
- Authenticated video meetings through Jitsi Meet.
- A small portal for invites, verification, roles, rooms, meetings, and audit records.
- Local backups and restore tooling.

Important limits in the current stage:

- It is invite-only by design. There is no public signup.
- Open federation with the public internet is not enabled.
- The portal is early-stage tooling and not yet packaged as a production web application image.
- It does not claim end-to-end encryption as a platform guarantee. Some clients may support encryption in specific cases, but Church policy should not assume it.

## How a Local Community Uses It

### Diocese

Examples:

- A diocesan clergy room for announcements, coordination, and pastoral support.
- Separate rooms for councils, commissions, and ministries.
- Controlled guest access for trusted external participants when needed.

Benefits:

- One place for diocesan communication without mixing with public social media.
- Clear membership and role rules.
- Audit records for administrative actions.

### Parish

Examples:

- A general parish room that is visible only to approved members.
- A catechumen or inquirer room with limited access.
- Ministry rooms for choir, outreach, youth, and education.
- Announcement-style rooms where only approved roles may post.

Benefits:

- New members join by invite and approval, not by stumbling into a public group.
- Rooms can be set to match parish life rather than one-size-fits-all chat apps.
- Clear separation between public parish outreach and internal parish life.

### Monastic Community

Examples:

- A monastic community room for internal coordination.
- Controlled rooms for guests, pilgrims, or volunteers where appropriate.
- Clergy-only or monastic-only rooms for sensitive discussions.

Benefits:

- Strong default privacy posture with administrator-controlled membership.
- Reduced reliance on third-party platforms and accounts.

## Membership and Verification

Orthodox Connect is designed around Church trust realities:

- People do not self-register.
- Administrators issue invites.
- New accounts are reviewed and approved.
- Higher-trust labels such as clergy or monastic status are granted only by an administrator decision.

This is not meant to replace pastoral judgment. It is meant to record and enforce the outcomes of pastoral and administrative decisions.

## Roles and Room Access

Rooms are intended to be scoped to Church needs, such as:

- Public-to-members spaces for normal parish life.
- Group-only spaces for ministries or committees.
- Clergy-only or monastic-only rooms for restricted discussions.
- Admin-only spaces for local operators.
- Invite-only rooms for limited situations.

Access is derived from verified roles and group membership, not from self-assigned labels.

## Video Meetings

Meetings are designed to be controlled:

- Anonymous public meeting creation is disabled.
- Meeting creation can be restricted to approved roles.
- Meeting access is tied to approved users or explicitly allowed guests.

This supports parish or diocesan policy, such as restricting official meetings to clergy or administrators while still allowing guest participation where appropriate.

## Local Deployment Options

Orthodox Connect is designed to be self-hosted:

- On a VPS managed by a trusted diocesan or parish operator.
- On a parish server.
- On a dedicated host controlled by a monastery.

The system is intended to work as a local communications platform even when not federated to other servers.

## Trusted Federation *(Planned, Not Enabled by Default)*

Federation means connecting separate Orthodox Connect servers so that specific shared rooms or channels can exist across communities, without merging the communities into one server.

Orthodox Connect follows a trusted federation model:

- Federation is not open by default.
- Each trusted server must be approved.
- Federation must be scoped to specific shared rooms or groups.
- Clergy or monastic verification does not automatically transfer between servers.
- Trust can be revoked quickly if needed.

Example uses:

- A shared clergy coordination room across a diocese and multiple parishes.
- A shared catechumen education room across a mission and a parent parish.
- A shared announcement channel for a set of trusted communities.

The goal is cooperation without losing local control.

## Why This Benefits the Church

- Local control: the Church controls the platform, policy, and data.
- Invite-only trust: membership starts from real-world relationships, not public signups.
- Role-aware access: rooms can reflect Church life, not generic social app defaults.
- Auditability: administrative actions are recorded for accountability.
- Reduced dependence: less reliance on commercial platforms and their incentives.
- Extensible path: trusted federation, Tor access, and library integration can be added deliberately later, not by accident.

## What to Consider Before Adopting

- Governance: who issues invites, who verifies, and who can create rooms and meetings.
- Operator trust: the host operator can access service metadata; treat it as a trusted role.
- Policy: what content belongs on the platform and what must stay offline.
- Incident response: how abuse, account compromise, and revocation will be handled.
- Backups: backups contain sensitive metadata and must be handled as private Church records.

## Next Steps for a Pilot

1. Choose a small initial community *(for example one parish or one monastic community)*.
2. Define admin roles and membership policy.
3. Set up invite-only onboarding.
4. Start with a small set of rooms and one meeting workflow.
5. Review outcomes, then expand.

