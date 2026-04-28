# Orthodox Connect Reverse Proxy Design

## 1. Reverse Proxy Goals

The reverse proxy is the public HTTP and HTTPS entrypoint for Orthodox Connect.

Goals:

- Route public browser traffic to the correct internal services.
- Keep PostgreSQL, Prosody internals, Converse.js internals, portal internals, and Jitsi internals off public host ports.
- Terminate HTTPS for portal, chat, meeting, and placeholder library routes.
- Preserve WebSocket support for Converse.js, Prosody browser transports, and Jitsi.
- Keep public domains configurable through environment variables.
- Avoid hard-coded real domains.
- Avoid manually committed TLS certificates.
- Apply service-appropriate security headers.
- Avoid logging secrets, tokens, private notes, or sensitive query strings.
- Keep Tor onion routing as a later design item that does not bypass normal authentication or authorization.

The reverse proxy must not become a source of identity, role, room, meeting, or verification policy. Those decisions belong to the portal and supporting services.

## 2. Preferred Reverse Proxy

Caddy is the preferred reverse proxy for Orthodox Connect.

Reasons:

- It is already used by the MVP Compose stack.
- It supports automatic ACME certificate management.
- It has simple reverse proxy configuration.
- It supports WebSocket proxying through normal reverse proxy routes.
- It can route by environment-configured hostnames.
- It keeps the deployment small and understandable for single-host operators.

Current reverse proxy service:

| Service         | Image            | Role |
| --------------- | ---------------- | ---- |
| `reverse-proxy` | `caddy:2-alpine` | Public HTTP and HTTPS routing. |

No alternate reverse proxy should be introduced unless a later design document records the reason and migration plan first.

## 3. Domain and Subdomain Model

Public hostnames come from environment variables.

| Variable         | Purpose |
| ---------------- | ------- |
| `ROOT_DOMAIN`    | Base domain for the deployment. |
| `PORTAL_DOMAIN`  | Portal and admin workflow hostname. |
| `CHAT_DOMAIN`    | Converse.js web chat and browser XMPP transport hostname. |
| `MEET_DOMAIN`    | Jitsi Meet web hostname. |
| `LIBRARY_DOMAIN` | Reserved placeholder for future library access. |

Rules:

- Do not hard-code real production domains in committed files.
- Do not add real partner or parish domains to docs.
- Hostnames should be explicit in `.env`.
- XMPP service domains such as `XMPP_DOMAIN` and `XMPP_MUC_DOMAIN` are protocol identities, not public HTTP routes by default.
- Jitsi internal XMPP domains are separate from the main Orthodox Connect XMPP domain.
- Federation DNS records must not be published until trusted federation is implemented and approved.

Suggested production pattern:

| Route Purpose | Example Shape |
| ------------- | ------------- |
| Portal        | `portal.example.invalid` |
| Chat          | `chat.example.invalid` |
| Meetings      | `meet.example.invalid` |
| Library       | `library.example.invalid` |

These are shapes only. They are not real deployment domains.

## 4. Local Development Hostname Model

Local development should use disposable hostnames and fake secrets.

Current local placeholder pattern:

| Variable         | Local Example |
| ---------------- | ------------- |
| `ROOT_DOMAIN`    | `orthodox-connect.localhost` |
| `PORTAL_DOMAIN`  | `portal.orthodox-connect.localhost` |
| `CHAT_DOMAIN`    | `chat.orthodox-connect.localhost` |
| `MEET_DOMAIN`    | `meet.orthodox-connect.localhost` |
| `LIBRARY_DOMAIN` | `library.orthodox-connect.localhost` |

Rules:

- Local development must not use production domains.
- Local development must not use production `.env` values.
- Local certificates, internal certificates, or browser exceptions may be acceptable for local testing.
- Real Let's Encrypt certificates require real public DNS names controlled by the operator.
- Local hostnames should be documented only where needed for setup or testing.

## 5. Public HTTPS Routing

The reverse proxy should route public HTTP and HTTPS traffic by hostname.

Current route model:

| Hostname Variable | Route Target | Purpose |
| ----------------- | ------------ | ------- |
| `PORTAL_DOMAIN`   | `portal:8000` | Portal and admin workflows. |
| `CHAT_DOMAIN`     | `converse:80` | Converse.js web chat frontend. |
| `CHAT_DOMAIN` with `/xmpp-websocket` | `prosody:5280` | Browser XMPP WebSocket. |
| `CHAT_DOMAIN` with `/http-bind` | `prosody:5280` | BOSH fallback. |
| `MEET_DOMAIN`     | `jitsi-web:80` | Jitsi Meet web interface. |
| `LIBRARY_DOMAIN`  | Placeholder response | Future library service route. |

Rules:

- Reverse proxy routes should use internal Docker service names, not host ports.
- HTTP should redirect to HTTPS in production where Caddy manages public certificates.
- Internal service ports should not be exposed directly unless a later reviewed design requires it.
- The library hostname should remain a disabled placeholder until library access control exists.
- Public anonymous meeting creation must remain disabled by Jitsi and portal policy.

## 6. Internal Upstream Routing

Internal upstreams should use Docker service names on private networks.

Current upstreams:

| Upstream       | Network Need | Public Exposure |
| -------------- | ------------ | --------------- |
| `portal:8000`  | `internal`   | Through `PORTAL_DOMAIN` only. |
| `converse:80`  | `internal`, `xmpp` | Through `CHAT_DOMAIN` only. |
| `prosody:5280` | `xmpp`       | Through chat transport paths only. |
| `jitsi-web:80` | `video`, `internal` | Through `MEET_DOMAIN` only. |

Rules:

- Do not route public traffic to PostgreSQL.
- Do not route public traffic to Prosody admin interfaces.
- Do not route public traffic to Jitsi internal Prosody, Jicofo, or JVB control paths.
- Do not route public traffic to Docker or host administration.
- The reverse proxy may join multiple Docker networks only to reach required upstreams.
- If a service is unhealthy or missing, the proxy should fail with a normal service error rather than exposing another backend.

## 7. WebSocket Routing Requirements

WebSocket routes are required for chat and Jitsi.

General requirements:

- Preserve `Upgrade` and `Connection` behavior through the proxy.
- Keep WebSocket traffic under HTTPS or WSS in production.
- Avoid exposing internal WebSocket ports directly.
- Avoid logging full URLs if query strings may contain tokens.
- Keep timeout behavior compatible with long-lived chat and meeting connections.

Current WebSocket needs:

| Feature | Public Path | Upstream |
| ------- | ----------- | -------- |
| Converse.js XMPP WebSocket | `/xmpp-websocket` on `CHAT_DOMAIN` | `prosody:5280` |
| Jitsi WebSocket support | `/xmpp-websocket`, `/colibri-ws/*`, `/conference-request/v1` on `MEET_DOMAIN` | `jitsi-web:80` |

WebSocket failures should be treated as service routing failures. They must not cause the operator to expose Prosody or Jitsi internals directly without a reviewed design.

## 8. Jitsi Routing Requirements

Jitsi web traffic should route through `MEET_DOMAIN`.

Requirements:

- Route `MEET_DOMAIN` to `jitsi-web:80`.
- Preserve Jitsi WebSocket paths.
- Keep Jitsi JWT authentication enabled.
- Keep anonymous public room creation disabled.
- Keep Jitsi internal Prosody, Jicofo, and internal control services private.
- Publish only JVB UDP media port where required by the selected Jitsi deployment.
- Keep security headers compatible with camera, microphone, and fullscreen use.
- Do not log JWT token bodies or sensitive query strings.

Current public Jitsi exposure:

| Public Route or Port | Purpose |
| -------------------- | ------- |
| `MEET_DOMAIN` over HTTPS | Jitsi Meet web interface. |
| `JITSI_JVB_PORT` UDP | Jitsi media transport. |

Meeting access remains controlled by portal-issued JWTs and Jitsi JWT validation. The reverse proxy should not make meeting access decisions beyond routing.

## 9. XMPP WebSocket and BOSH Routing Requirements

Browser XMPP access should route through `CHAT_DOMAIN`.

Current routes:

| Public Path       | Upstream        | Purpose |
| ----------------- | --------------- | ------- |
| `/xmpp-websocket` | `prosody:5280`  | Preferred browser XMPP transport. |
| `/http-bind`      | `prosody:5280`  | BOSH fallback for browser clients. |

Rules:

- Prosody `5280/tcp` should remain internal.
- Native XMPP client ports should remain closed until a client support design approves them.
- Public XMPP registration remains disabled.
- Open XMPP federation remains disabled.
- BOSH and WebSocket routes must not expose Prosody admin endpoints.
- Converse.js configuration should point to the public HTTPS and WSS routes, not internal Docker names.
- Reverse proxy logs should avoid query strings and credentials.

The portal remains the source of truth for identity and room policy. Reverse proxy routing does not grant XMPP account access.

## 10. Security Headers

Security headers should be applied per service so they reduce risk without breaking required browser features.

Baseline headers:

| Header | Direction |
| ------ | --------- |
| `Strict-Transport-Security` | Enable for production HTTPS routes. |
| `X-Content-Type-Options` | Use `nosniff`. |
| `X-Frame-Options` | Use `DENY` for portal where practical, `SAMEORIGIN` for chat and meeting pages where needed. |
| `Referrer-Policy` | Use a strict origin policy. |
| `Permissions-Policy` | Deny unused browser permissions by default. |
| `Server` | Remove or suppress where practical. |

Service-specific guidance:

| Route | Header Notes |
| ----- | ------------ |
| Portal | Deny camera and microphone. Use the strictest frame policy practical. |
| Chat | Deny camera and microphone unless a later chat feature needs them. |
| Jitsi | Allow camera, microphone, and fullscreen for the meeting origin. |
| Library placeholder | Use portal-style restrictive headers until the service exists. |

Headers must not be used as the only authorization control. Portal, Prosody, and Jitsi must still enforce authentication and authorization.

## 11. Rate Limiting Strategy

Rate limiting is required for production hardening, but it should be implemented carefully.

Priority routes for future rate limits:

- Portal login.
- Invite redemption.
- Account recovery when implemented.
- Verification request submission.
- Meeting token issuance.
- XMPP browser transport connection attempts.
- Jitsi join attempts.

Policy:

- Prefer portal-level rate limiting for identity-aware actions.
- Use reverse-proxy rate limits only where route-level traffic control is useful.
- Rate limit by account, token, session, route, and source metadata where practical.
- Tor onion traffic should not rely only on IP-based rate limiting.
- Rate limit failures should not reveal whether an account, invite, or meeting exists.
- Rate limit events should create security or audit records where useful.

Caddy core does not provide a full identity-aware rate limiting system by itself. Any plugin or external service choice should be reviewed before implementation.

## 12. Access Logging Policy

Reverse proxy logs are useful for operations, but they can expose sensitive metadata.

Log intentionally:

- Service start, stop, and configuration errors.
- Upstream failures.
- TLS and certificate renewal failures.
- WebSocket routing failures.
- Coarse HTTP status and path data needed for troubleshooting.

Avoid logging:

- Full query strings.
- Invite tokens.
- Recovery tokens.
- Jitsi JWT bodies.
- Session cookies.
- Passwords.
- Full request bodies.
- `.env` contents.
- Private room or meeting details beyond what is needed for operations.

Retention guidance:

- Keep reverse proxy access logs short-lived.
- Treat logs as sensitive records.
- Do not commit logs to Git.
- Do not paste production logs into public support channels without review.
- Do not back up routine reverse proxy logs unless the deployment has a written reason.

## 13. TLS Certificate Handling

Caddy should manage public TLS certificates automatically for real production hostnames.

Rules:

- Do not commit TLS private keys.
- Do not commit ACME account keys.
- Do not commit certificate stores.
- Do not manually add production certificates to the repository.
- Use `ACME_EMAIL` for certificate contact configuration.
- Store Caddy certificate data in the reverse proxy data volume.
- Back up Caddy certificate data only through operator-controlled backups where required.
- Rotate or replace certificates if private keys are exposed.

Local development:

- Local `.localhost` names may not use public ACME certificates.
- Operators may use Caddy local certificates, browser exceptions, or local-only TLS where needed.
- Local TLS material must not be treated as production trust material.

Production:

- Public DNS must point to the host before certificate issuance.
- Ports `80/tcp` and `443/tcp` must be reachable where Caddy uses HTTP-01 or normal HTTPS service.
- Operators should verify certificate issuance and renewal before inviting real users.

## 14. Tor and Onion Routing Placeholder

Tor onion access is future scope and must not be enabled by this design.

Planned direction:

- Add onion access only after the normal HTTPS deployment is stable.
- Route onion portal traffic to the same portal service.
- Route onion chat traffic to Converse.js and Prosody browser transports.
- Avoid onion access for Jitsi media by default.
- Do not expose PostgreSQL, Prosody native client ports, Caddy admin APIs, Docker, or host admin ports through onion services.
- Use separate onion hostnames from public DNS hostnames.
- Keep onion private keys out of Git.

Onion access must use the same invite-only registration, manual verification, role checks, suspension, and audit controls as normal HTTPS access.

## 15. Failure Handling

Reverse proxy failures should fail closed and be easy for operators to diagnose.

Failure cases:

| Failure | Expected Handling |
| ------- | ----------------- |
| Missing hostname variable | Caddy config should fail clearly or route should remain unavailable. |
| Upstream service down | Public route returns a service error, not another backend. |
| TLS issuance failure | HTTP/HTTPS route remains unavailable until DNS, ports, or ACME settings are fixed. |
| WebSocket failure | Chat or meeting transport fails without exposing internal ports. |
| Bad route match | Default should not expose an unintended service. |
| Jitsi media issue | Web route may load, but media failure should be diagnosed through Jitsi and JVB logs. |
| Prosody transport issue | Chat frontend may load, but login or room traffic fails until Prosody route is fixed. |

Operator checks:

- Confirm `docker compose config` renders.
- Confirm `reverse-proxy` is running.
- Confirm public HTTP and HTTPS ports are reachable.
- Confirm Caddy logs do not show certificate or upstream errors.
- Confirm portal, chat, XMPP browser transport, and meeting routes respond.
- Confirm internal service ports remain private.

Failure handling must not weaken registration, federation, portal admin checks, Prosody access checks, or Jitsi JWT authentication.

## 16. Rollback Plan

Reverse proxy rollback should restore the last known-good routing state without changing application data.

Rollback steps:

1. Stop or isolate the public route if current routing exposes the wrong service.
2. Preserve current Caddyfile, Caddy logs, and relevant operator notes for review.
3. Restore the last known-good Caddyfile.
4. Confirm public hostnames still come from environment variables.
5. Confirm no real domains, certificates, or secrets were committed.
6. Confirm portal routes only to `portal:8000`.
7. Confirm chat routes only to `converse:80` and `prosody:5280` for browser XMPP paths.
8. Confirm meeting routes only to `jitsi-web:80`.
9. Confirm library route remains disabled until a library service is implemented.
10. Confirm internal service ports remain private.
11. Confirm public registration remains disabled.
12. Confirm open federation remains disabled.
13. Restart or reload the reverse proxy.
14. Run route checks with disposable data only.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
