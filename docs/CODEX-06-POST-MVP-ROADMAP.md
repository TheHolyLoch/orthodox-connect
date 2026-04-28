# Orthodox Connect Post-MVP Roadmap

## Purpose

This roadmap lists post-MVP work only. It does not add services, change Docker behavior, or define implementation details beyond planning.

Status values:

- `required`: Needed before the project should be treated as production-ready for normal parish use.
- `optional`: Useful for some deployments, but not needed for every instance.
- `deferred`: Later work that should wait until core operations are stable.

## Roadmap Items

| Item                                      | Status   | Dependencies                                                                                     | Risks                                                                                                  |
| ----------------------------------------- | -------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| Trusted federation between parish/group servers | deferred | Stable local identity model, Prosody account provisioning, room policy sync, federation allowlist design. | Federation expands spam, impersonation, moderation, metadata, support, and policy complexity.           |
| Tor onion access                          | optional | Stable HTTPS deployment, clear onion hostname plan, operator key handling, backup policy.          | Onion keys are sensitive, abuse handling is harder, Jitsi over Tor may not be practical.                |
| PDF/ebook library integration             | optional | Final library service choice, storage sizing, role-based collection policy, backup coverage.       | Copyright mistakes, storage growth, access-control drift from chat roles, sensitive document exposure.  |
| IRC fallback or bridge                    | deferred | Clear use case, bridge software review, identity mapping rules, moderation policy.                 | IRC weakens identity guarantees, may leak room names or messages, increases abuse and support load.     |
| Mobile app strategy                       | required | Prosody account provisioning, client compatibility testing, TLS and push notification decision.    | External clients may hide verification labels, mis-handle encryption, or confuse non-technical users.   |
| Moderation tooling                        | required | Room policy model, audit events, admin role scopes, message retention policy.                      | Overbroad moderator powers, insufficient audit trails, inconsistent enforcement across clients.         |
| Abuse reporting                           | required | User-facing reporting UI, admin review workflow, audit events, privacy policy.                     | Reports may include sensitive pastoral context, false reports, retention and access-control mistakes.   |
| Account recovery improvements             | required | Portal login workflow, email or out-of-band recovery channel, admin approval policy.               | Recovery can bypass verification, expose account existence, or enable takeover of privileged accounts.  |
| Export/import and migration               | required | Stable schema, tested backups, service inventory, versioned migration format.                      | Incomplete exports, broken restore paths, secret leakage, incompatible data between versions.           |
| Monitoring and health checks              | required | Production portal packaging, service health endpoints, log policy, operator alerting channel.      | Monitoring can leak metadata, create noisy alerts, or miss application-level failures.                  |
| Disaster recovery                         | required | Tested local backups, restore runbook, off-host backup decision, operator access control.          | Untested restores, stale backups, leaked backup archives, unclear ownership during incidents.           |
| Security review checklist                 | required | Current security model, deployment docs, admin workflows, dependency inventory.                    | Checklist can become stale, miss operational risks, or create false confidence without manual review.   |

## Notes

- Federation must stay disabled until allowlists, moderation duties, and external identity labeling are designed.
- Tor access should not weaken existing authentication, authorization, audit, or backup rules.
- Library access should remain separate from chat room access unless the portal has explicit collection policy support.
- IRC should remain a fallback or bridge only, not the primary trust or identity layer.
- Mobile support should start with tested XMPP client guidance before any custom mobile application is considered.
- Disaster recovery should be tested against disposable data before any production deployment depends on it.
