# Orthodox Connect Performance and Scaling

## 1. Performance Goals

Orthodox Connect should stay simple, reliable, and understandable for a small self-hosted deployment before adding scaling complexity.

Goals:

- Keep the MVP usable for a parish, monastery, mission, diocese pilot, or trusted small community.
- Keep portal admin workflows responsive under normal invite, verification, room, meeting, and audit use.
- Keep chat connection handling stable for approved users.
- Keep Jitsi meetings reliable within the host's CPU, memory, and bandwidth limits.
- Keep PostgreSQL, Prosody, Jitsi, reverse proxy, and backup storage observable before scaling.
- Prefer vertical scaling and operational tuning before horizontal scaling.
- Avoid adding external infrastructure until real measurements justify it.
- Keep public registration disabled and open federation disabled while scaling.
- Preserve backup and restore reliability as data grows.

This document is a design document only. It does not modify Docker services or implement scaling changes.

## 2. Expected Usage Patterns

Expected MVP usage is uneven and community-driven.

Likely patterns:

- Low daily portal use with short bursts during onboarding, verification, and room administration.
- Persistent chat sessions from browser clients and future native XMPP clients.
- Group chat activity around parish, diocesan, monastic, ministry, catechism, or event schedules.
- Higher Jitsi load during scheduled meetings, classes, parish council meetings, clergy coordination, or events.
- Short admin bursts for invite creation, verification review, audit review, and meeting setup.
- Backup activity during scheduled local backup windows.
- Occasional restore tests in staging or disposable environments.

Scaling decisions should be based on measured service behavior, not assumed community size.

## 3. MVP Capacity Assumptions

The MVP assumes a single-host Docker Compose deployment.

Baseline assumptions:

- One reverse proxy routes public HTTP and HTTPS traffic.
- One PostgreSQL database stores portal state.
- One Prosody service handles XMPP and MUC.
- One Converse.js frontend serves static web chat files.
- One Jitsi stack handles authenticated meetings.
- One local backup path stores timestamped backups.
- Internal service ports remain private.
- Jitsi JVB publishes only the media port required for the selected deployment.

Capacity assumptions:

- The portal should have light load compared with chat and video.
- PostgreSQL load should be modest unless audit, admin lists, or future reporting grow.
- Prosody capacity depends on concurrent sessions, MUC rooms, message archive settings, and future external clients.
- Converse.js static serving is expected to be low cost.
- Jitsi is expected to be the main CPU, memory, and bandwidth driver.
- Backup size grows with PostgreSQL, Prosody data, Jitsi config, reverse proxy data, and future uploads.

No real usage data is defined in this repository. Operators should measure each deployment before making production promises.

## 4. Bottleneck Analysis

### Portal

Potential bottlenecks:

- Slow admin lists for users, invites, verification requests, rooms, meetings, or audit events.
- Missing indexes for new query patterns.
- Template rendering or API routes doing repeated policy checks inefficiently.
- Long-running admin actions blocking request handling.
- Future authentication, recovery, and moderation workflows increasing write volume.

Mitigations:

- Keep admin lists paginated.
- Filter large lists by status, scope, and date.
- Add indexes only after query patterns are known.
- Keep policy checks server-side and shared.
- Move expensive future work into reviewed background jobs only when needed.

### Postgres

Potential bottlenecks:

- Audit event growth.
- Invite, verification, room, and meeting list queries without useful filters.
- Backup or restore operations competing with live use.
- Database storage growth from future features.
- Poor environment separation causing accidental production-size data in staging or local development.

Mitigations:

- Keep audit queries newest-first and indexed by common filters.
- Monitor database size and backup duration.
- Run backups during low-usage windows.
- Test restores on a schedule.
- Keep production data out of lower environments unless scrubbed and approved.

### Prosody

Potential bottlenecks:

- Concurrent XMPP sessions.
- MUC room count and active room traffic.
- Message archive storage if enabled.
- Browser WebSocket or BOSH connection count.
- Future native XMPP clients increasing connection diversity.
- Future trusted federation increasing remote traffic and moderation load.

Mitigations:

- Keep public registration disabled.
- Keep open federation disabled.
- Keep native client ports closed until reviewed.
- Review message archive settings per room type.
- Monitor connection failures, authentication failures, and MUC errors.
- Keep room access policy derived from portal data.

### Converse and Web Chat

Potential bottlenecks:

- Static asset delivery under repeated reloads.
- Browser WebSocket or BOSH transport failures.
- Client-side performance in rooms with large histories.
- Users on mobile browsers with limited resources.
- Cache behavior that serves stale configuration.

Mitigations:

- Serve Converse.js through Caddy.
- Keep frontend configuration simple and environment-driven.
- Prefer WebSocket with BOSH as fallback where configured.
- Avoid loading large room histories by default until retention and UX are reviewed.
- Test mobile browser behavior with realistic rooms before broad rollout.

### Jitsi

Potential bottlenecks:

- CPU use from video conferences.
- Memory use from meeting components.
- Upload bandwidth from JVB media forwarding.
- Network quality and packet loss.
- Large meetings or many simultaneous meetings.
- Screen sharing and high-definition video increasing load.
- JWT validation or meeting token issuance failures under spikes.

Mitigations:

- Treat Jitsi as the primary scaling constraint.
- Keep meeting creation role-gated.
- Keep guests explicit and expiring.
- Use short-lived tokens.
- Size the host for expected meeting patterns.
- Monitor Jicofo, JVB, meeting join failures, and media bridge health.
- Avoid promising large public events until tested.

### Reverse Proxy

Potential bottlenecks:

- TLS handshake load.
- WebSocket connection handling.
- Large Jitsi route traffic.
- Misrouted upstreams causing retries or failures.
- Access logs growing too quickly.
- Certificate renewal failures.

Mitigations:

- Keep Caddy as the single public HTTP and HTTPS entrypoint.
- Route only reviewed public services.
- Keep PostgreSQL, Prosody internals, and Jitsi internals private.
- Monitor upstream errors and TLS renewal.
- Avoid logging sensitive query strings.
- Keep disabled future routes as placeholders only.

## 5. Vertical Scaling Strategy

Vertical scaling is the preferred first step.

Strategy:

- Increase CPU, memory, disk, and bandwidth on the existing host before adding distributed services.
- Prioritize CPU and bandwidth for Jitsi-heavy deployments.
- Prioritize disk and backup storage for deployments with message archive, audit growth, or future library files.
- Prioritize memory for PostgreSQL, Prosody, and Jitsi stability under concurrent use.
- Keep Docker Compose service layout unchanged until measurement proves a need.
- Test backup and restore after increasing storage or changing host class.

Vertical scaling should be paired with monitoring. Larger hardware does not fix bad room policy, unbounded logs, stale backups, or public exposure mistakes.

## 6. Horizontal Scaling Strategy

Horizontal scaling is future work.

Possible future directions:

- Separate PostgreSQL onto a managed or dedicated database host.
- Separate Jitsi onto a host with stronger CPU and network capacity.
- Add multiple JVB instances for larger meeting loads.
- Put the portal behind a load balancer after session storage and health checks are implemented.
- Split Prosody only after account provisioning, room sync, federation policy, and operational monitoring are mature.
- Use object storage or dedicated storage only after backup and privacy rules are reviewed.

Prerequisites:

- Service health checks.
- Centralized or environment-safe session handling.
- Documented backup and restore per service.
- Monitoring for each service boundary.
- Tested rollback path.
- No public registration.
- No open federation unless a later trusted federation plan is implemented.

Horizontal scaling should not be introduced to solve unknown problems.

## 7. Caching Considerations

Caching should be conservative because Orthodox Connect is role-aware and invite-only.

Safe caching candidates:

- Static Converse.js assets.
- Static portal assets when a production portal package exists.
- Public placeholder pages that contain no private data.
- Reverse proxy TLS and normal browser cache behavior for static assets.

Avoid caching:

- Portal admin pages.
- User status pages.
- Invite redemption responses.
- Verification request or decision pages.
- Room access decisions.
- Meeting token responses.
- Audit event views.
- API responses containing user, role, group, room, meeting, or audit data.

Caching rules:

- Permission-sensitive data should be computed from portal state.
- Cache invalidation must not be required to enforce suspension, role removal, invite revocation, or meeting access changes.
- If caching is added later, it must fail closed and respect admin role checks.

## 8. Connection Limits

Connection limits should protect the host without blocking normal parish use.

Areas to watch:

- Browser HTTP connections to Caddy.
- WebSocket and BOSH connections to Prosody.
- Jitsi web and media connections.
- PostgreSQL client connections from portal workflows.
- Admin UI sessions.
- Future native XMPP clients.

Policy:

- Set limits only after measuring normal behavior.
- Prefer account-aware and route-aware limits over broad IP-only limits where possible.
- Rate limit invite redemption, login, recovery, and meeting token issuance when those workflows are implemented.
- Keep internal service ports private rather than relying on public connection limits.
- Document any limit that can affect non-technical users during services or meetings.

Tor access, if implemented later, will need separate review because IP-based limits are weaker there.

## 9. Media Bandwidth Considerations

Jitsi media is the largest expected bandwidth consumer.

Bandwidth drivers:

- Number of active meetings.
- Number of participants per meeting.
- Camera quality and resolution.
- Screen sharing.
- Audio-only versus video use.
- Participant network quality.
- JVB public media traffic.

Operational guidance:

- Do not promise large meetings until tested on the actual host and network.
- Prefer scheduled tests before major parish, diocesan, or monastic events.
- Keep official meeting creation role-gated.
- Encourage audio-only or lower video quality if the host or user networks are constrained.
- Monitor JVB health, packet loss symptoms, CPU, memory, and outbound bandwidth.
- Keep Jitsi separate from sensitive portal and database operations where future scaling requires it.

Jitsi over Tor is not part of the current plan and should not be promised.

## 10. Storage Growth Considerations

Storage growth comes from persistent service data and backups.

Current storage sources:

- PostgreSQL portal data.
- Portal audit events.
- Prosody data.
- Prosody MUC state and possible message archive.
- Jitsi configuration and generated state.
- Reverse proxy ACME and runtime data.
- Local backup output.
- Logs retained by Docker or operator policy.

Future storage sources:

- Portal uploads if added.
- Abuse report evidence if moderation tooling is implemented.
- Library metadata and files if the library service is added.
- Tor onion keys if onion access is added.
- IRC service data if fallback or bridge support is added.

Controls:

- Keep logs short-lived.
- Keep backup output outside Git.
- Review message archive settings before production use.
- Monitor backup size and restore duration.
- Define retention before adding uploads, library files, or moderation evidence.
- Keep storage checks in monthly admin tasks.

## 11. Monitoring Requirements

Monitoring should start with local, operator-friendly checks.

Required MVP checks:

- Container status for expected services.
- Reverse proxy route health.
- TLS certificate renewal status.
- PostgreSQL connectivity.
- Portal migration and admin workflow health.
- Prosody WebSocket or BOSH transport health.
- Prosody authentication and MUC errors.
- Converse.js route loading.
- Jitsi web, Jicofo, JVB, and meeting join health.
- Backup success, backup age, and restore test status.
- Disk usage and backup storage usage.
- Repeated authentication, invite, or meeting token failures.

Future checks:

- Portal health endpoint after production packaging.
- Structured application metrics.
- Jitsi meeting capacity metrics.
- Prosody connection and room metrics.
- Alerting for backup failure, disk pressure, TLS renewal failure, and service outages.

Monitoring must not collect message bodies, invite tokens, recovery tokens, JWT bodies, session cookies, `.env` contents, or private notes.

## 12. Stress Testing Approach

Stress testing should use fake data and staged environments.

Approach:

1. Define the workflow being tested.
2. Use local or staging data only.
3. Test one service path at a time before testing the full stack.
4. Measure baseline idle resource use.
5. Measure portal list and write workflows with fake users, invites, verification requests, rooms, meetings, and audit events.
6. Measure Prosody browser transport and room behavior with test accounts.
7. Measure Converse.js loading and room UX with realistic fake room sizes.
8. Measure Jitsi with scheduled test meetings and explicit participant counts.
9. Measure backup duration and restore success after load tests.
10. Record host size, environment, test data shape, service versions, bottlenecks, and rollback steps.

Rules:

- Do not use real parish, diocesan, monastic, invite, verification, meeting, or chat data for casual load tests.
- Do not enable public registration for testing.
- Do not enable open federation for testing.
- Do not publish staging links to ordinary users.
- Do not treat synthetic tests as production guarantees.

## 13. Scaling Risks

Scaling risks:

- Adding infrastructure before measuring the actual bottleneck.
- Making backups incomplete after moving data or services.
- Losing the portal as the source of truth.
- Widening public exposure while trying to improve performance.
- Serving stale permissions from caches.
- Increasing Jitsi capacity without enough bandwidth.
- Growing logs, audit events, message archives, or backups beyond available storage.
- Copying production data into staging or local development for testing.
- Overloading administrators with monitoring noise.
- Creating split-brain room, role, or meeting state across services.
- Making rollback harder by distributing services too early.

Scaling must not weaken registration, verification, room access, meeting authentication, logging privacy, or backup rules.

## 14. Rollback Plan

Scaling rollback should return the deployment to the last known-stable service layout without deleting trust records.

Rollback steps:

1. Stop the scaling experiment or affected public route if service behavior is unsafe.
2. Preserve logs, audit events, backup manifests, and test notes for review.
3. Revert the scaling configuration or host change.
4. Restore service data from same-environment backups only if needed.
5. Confirm public registration remains disabled.
6. Confirm open federation remains disabled.
7. Confirm internal service ports remain private.
8. Confirm Jitsi authentication remains enabled.
9. Confirm portal admin routes require admin roles.
10. Confirm portal database state remains the source of truth.
11. Confirm chat, meetings, backups, and restore tests still work.
12. Rotate secrets if any scaling test exposed configuration, logs, tokens, or backup data.
13. Record what was rolled back and what measurement triggered the decision.

Rollback must not delete users, groups, roles, invites, verification records, rooms, meetings, audit events, backups, Prosody data, Jitsi state, reverse proxy data, or unrelated service configuration.
