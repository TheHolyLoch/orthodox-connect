# Orthodox Connect Disaster Recovery

## Disaster Recovery Goals

Disaster recovery should let trusted operators restore Orthodox Connect after service failure, data loss, host loss, DNS failure, or operator error without weakening access control.

Goals:

- Restore portal identity, roles, verification, rooms, meetings, and audit records.
- Restore chat service data and configuration where available.
- Restore Jitsi configuration and authenticated meeting access.
- Keep secrets out of Git.
- Keep emergency contact details outside public docs.
- Keep public registration disabled after restore.
- Keep federation disabled unless a later trusted federation policy explicitly enables it.
- Test restores before production depends on them.
- Document what can be restored, what may be lost, and who is responsible for each step.

Disaster recovery is not a replacement for moderation, account recovery, pastoral emergency procedures, or civil emergency communication.

## Failure Scenarios

Operators should plan for:

- Reverse proxy outage.
- TLS certificate renewal failure.
- DNS misconfiguration or registrar outage.
- Host failure or VPS provider outage.
- Disk full condition.
- PostgreSQL corruption.
- Bad database migration.
- Prosody data loss or configuration error.
- Jitsi component failure.
- Portal admin UI or CLI failure.
- Backup script failure.
- Restore script failure.
- Secret leakage.
- Accidental deletion of users, rooms, or roles.
- Compromised administrator account.
- Loss of operator access.
- Network censorship or blocking of the public endpoint.

Each scenario should have an owner, a communication path, and a decision point for whether to restore, rollback, or temporarily disable a service.

## Recovery Priorities

Recovery should restore trust and identity before convenience features.

Priority order:

1. Operator access to the host or replacement host.
2. `.env` and operator-owned secrets from secure storage.
3. PostgreSQL portal data.
4. Portal admin workflow.
5. Reverse proxy and TLS routing.
6. Prosody configuration and data.
7. Converse.js chat frontend.
8. Jitsi configuration and authenticated meeting access.
9. Local backup tooling.
10. Monitoring and health checks.
11. Library data when the library exists.
12. Tor or IRC fallback if those later features exist.

If identity data cannot be trusted, operators should keep chat and meetings offline until portal roles, suspension state, and room access state are reviewed.

## Backup Inventory

The backup inventory should list every item needed to restore the instance.

Required current backup items:

| Item                   | Source                         | Sensitivity | Notes |
| ---------------------- | ------------------------------ | ----------- | ----- |
| PostgreSQL logical dump | `postgres`                    | High        | Portal identity, invites, roles, rooms, meetings, audit events. |
| Prosody data           | `prosody_data` volume          | High        | XMPP state, room data, local service state. |
| Prosody config         | `prosody/`                     | Medium      | Committed config plus operator environment. |
| Jitsi web config       | `jitsi_web_config` volume      | High        | Generated runtime configuration. |
| Jitsi Prosody config   | `jitsi_prosody_config` volume  | High        | Internal meeting auth state. |
| Jicofo config          | `jitsi_jicofo_config` volume   | High        | Internal Jitsi component state. |
| JVB config             | `jitsi_jvb_config` volume      | High        | Media bridge runtime state. |
| Reverse proxy data     | `reverse_proxy_data` volume    | High        | ACME account and certificate data if managed by Caddy. |
| Reverse proxy config   | `reverse_proxy_config` volume  | Medium      | Caddy runtime config. |
| `.env`                 | Operator secret storage        | High        | Must not be committed to Git. |
| Backup manifests       | Backup output directory        | Medium      | Should not expose secret values. |

Future backup items:

- Portal uploads, if uploads are added.
- Library metadata and files, if library service is added.
- Tor onion service keys, if onion access is added and stable onion hostnames are required.
- IRC service config and account state, if IRC fallback is added.

Backups should be stored outside Git and protected like sensitive community records.

## Restore Order

Restore order should reduce the chance of running services against incomplete or mismatched state.

Recommended restore order:

1. Prepare replacement host or clean local restore target.
2. Install required runtime outside this document's scope.
3. Restore repository checkout from Git.
4. Restore `.env` from operator secret storage.
5. Restore Docker volumes or named backup directories.
6. Restore PostgreSQL logical dump.
7. Start PostgreSQL only.
8. Run portal migrations or schema checks if required.
9. Start portal and confirm admin access.
10. Start reverse proxy.
11. Start Prosody and confirm browser transport paths.
12. Start Converse.js frontend.
13. Start Jitsi components.
14. Run health checks.
15. Review audit events, roles, room access, and suspension state.
16. Notify users only after administrator review is complete.

If any restored secret is suspected to be exposed, rotate that secret before public service resumes.

## Offline Emergency Access Plan

Offline emergency access should let operators coordinate while the main site is down.

Plan:

- Maintain an operator-controlled contact list outside the repository.
- Keep at least two trusted administrators reachable through an out-of-band method.
- Keep recovery instructions available outside the production host.
- Keep recent backup locations documented outside the production host.
- Use a fallback read-only notice channel only for non-sensitive updates.
- Use IRC fallback only if it has been reviewed and deployed later.
- Use Tor onion access only if it has been reviewed and deployed later.

Offline access must not be used to approve new users, grant clergy status, grant monastic status, or bypass portal audit records. Any emergency decision made outside the system should be recorded in the portal audit trail after service is restored.

## Admin Emergency Contacts Model

Emergency contacts should be managed by operators, not committed to this repository.

Contact model:

- Primary technical operator.
- Secondary technical operator.
- Primary parish or group administrator.
- Secondary parish or group administrator.
- Diocesan or higher-scope contact where applicable.
- Hosting provider account owner.
- DNS registrar account owner.
- Backup storage owner.

For each contact, operators should store:

- Name or role.
- Contact method.
- Scope of authority.
- Expected response window.
- Backup contact path.
- Date last verified.

Emergency contact records should be stored in an operator-controlled location with access limited to trusted administrators.

## DNS Failure Plan

DNS failure can block portal, chat, XMPP browser transports, and Jitsi web access even when the host is healthy.

Plan:

1. Confirm whether failure is DNS, reverse proxy, host, or certificate related.
2. Check registrar and DNS provider status through an operator account.
3. Confirm records for portal, chat, meet, XMPP, and root domains.
4. Avoid adding temporary public domains unless the operator can secure TLS and update user guidance safely.
5. Use existing offline emergency contacts to tell users the service is unavailable.
6. Restore normal DNS records when provider access returns.
7. Review certificate renewal after DNS is stable.

Do not publish unreviewed domains or IP-only access for normal users. Temporary endpoints can create impersonation and TLS risks.

## Host Failure Plan

Host failure includes VPS outage, disk failure, provider account loss, or unrecoverable operating system damage.

Plan:

1. Confirm the host is unavailable through provider status and local checks.
2. Stop automated restore attempts if data corruption is suspected.
3. Provision a replacement host using the same deployment assumptions.
4. Restore the repository checkout.
5. Restore `.env` and required secrets from operator storage.
6. Restore backup volumes and PostgreSQL dump.
7. Start services in the documented restore order.
8. Update DNS only after the replacement host is ready.
9. Confirm TLS issuance or restored Caddy data.
10. Review logs and audit events before public user notice.

If the old host may be compromised, rotate secrets before returning service to users.

## Database Corruption Plan

PostgreSQL contains the portal trust state and should be treated as the highest recovery priority.

Plan:

1. Stop portal workflows that write to the database.
2. Preserve current database volume for later review.
3. Identify the most recent known-good logical dump.
4. Restore to a disposable environment first where possible.
5. Check migrations, users, roles, invites, verification records, rooms, meetings, and audit events.
6. Restore to production only after the dump passes basic checks.
7. Review events between the backup timestamp and failure time.
8. Recreate missing admin actions manually only after review.
9. Notify affected administrators of possible data loss.

If corruption followed a bad migration, restore the previous backup and rollback the migration plan before restarting portal workflows.

## Prosody and XMPP Recovery Plan

Prosody recovery should restore chat access without bypassing portal policy.

Plan:

1. Restore Prosody configuration.
2. Restore Prosody data volume.
3. Confirm `XMPP_REGISTRATION_ENABLED=false`.
4. Confirm federation remains disabled unless a later policy explicitly enabled it.
5. Start Prosody after PostgreSQL and portal state are reviewed.
6. Confirm browser WebSocket or BOSH routes through Caddy.
7. Confirm MUC rooms do not grant access beyond portal policy.
8. Review suspended users and room memberships.
9. Keep native XMPP ports closed unless the deployment intentionally supports them.

If Prosody data cannot be restored, rebuild chat rooms from portal policy where possible and document message history loss.

## Jitsi Recovery Plan

Jitsi recovery should restore authenticated meetings without public room creation.

Plan:

1. Restore Jitsi configuration volumes.
2. Restore Jitsi JWT variables from `.env`.
3. Confirm `JITSI_ENABLE_AUTH=1`.
4. Confirm `JITSI_ENABLE_GUESTS=0` for MVP policy.
5. Start `jitsi-prosody`, `jitsi-jicofo`, `jitsi-jvb`, and `jitsi-web` in dependency order where practical.
6. Confirm the reverse proxy route for the meeting hostname.
7. Issue a test meeting token through the portal.
8. Confirm unauthorized users cannot create public rooms.
9. Confirm old compromised meeting links or tokens are no longer valid if secrets were rotated.

If Jitsi cannot be recovered quickly, keep portal and chat online and mark meetings unavailable through the approved user notice path.

## Portal Recovery Plan

Portal recovery restores the trust control plane.

Plan:

1. Restore PostgreSQL first.
2. Restore `.env` values needed by portal.
3. Confirm `PORTAL_SECRET_KEY` source.
4. Run portal database checks or migrations as required.
5. Start the portal admin workflow.
6. Confirm an approved admin can view users, groups, roles, invites, verification requests, rooms, and audit events.
7. Confirm suspended users remain suspended.
8. Confirm public registration remains unavailable.
9. Confirm meeting token issuance remains role-gated.
10. Record recovery actions in audit events where the portal supports it.

If portal login or admin UI is unavailable, operators should keep new invites, verification, role changes, and meeting creation paused.

## Library Recovery Placeholder

Library recovery is later scope because no library service is currently deployed.

Future plan:

- Restore library metadata store.
- Restore uploaded files.
- Restore collection access policy.
- Confirm no anonymous public access.
- Confirm collection permissions match portal roles or explicit library policy.
- Confirm copyright and permission metadata survived restore.
- Test search without exposing restricted collections.
- Restore library only after portal identity and role state is trusted.

Library backups may be large and sensitive. They should not be added to the current restore runbook until the library service exists.

## Test Restore Schedule

Restore tests should happen before production use and on a regular schedule.

Recommended schedule:

- Monthly local backup creation check.
- Quarterly restore test with disposable data.
- Restore test before major upgrades.
- Restore test after backup script changes.
- Restore test after changing PostgreSQL, Prosody, Jitsi, reverse proxy, or volume layout.
- Annual review of operator emergency contacts and backup locations.

Each test should record:

- Backup timestamp.
- Restore target.
- Services restored.
- Checks passed.
- Data loss found.
- Secrets rotated, if any.
- Operator who performed the test.
- Follow-up actions.

Do not use real parish data in casual test environments unless the operator has approved the handling risk.

## Rollback Plan

Rollback should return the system to a known-good state without deleting evidence or unrelated data.

Rollback steps:

1. Stop affected public routes or services.
2. Preserve current data, logs, and backup manifests for review.
3. Identify the last known-good backup or configuration.
4. Restore only the affected service when possible.
5. Restore the whole stack only when service-specific rollback is unsafe.
6. Rotate exposed or possibly exposed secrets.
7. Confirm public registration remains disabled.
8. Confirm federation remains disabled unless intentionally enabled by reviewed policy.
9. Confirm admin roles, verification records, room access, and suspension state.
10. Record the rollback decision and result.
11. Notify users after administrator review.

Rollback must not delete portal users, roles, verification records, rooms, meeting records, audit events, backups, or unrelated service data.
