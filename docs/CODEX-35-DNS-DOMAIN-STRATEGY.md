# Orthodox Connect DNS and Domain Strategy

## 1. Domain Goals

DNS and domain configuration should keep Orthodox Connect reachable, understandable, and recoverable without exposing internal services.

Goals:

- Use operator-controlled hostnames for production.
- Keep hostnames configured through environment variables.
- Keep public HTTP and HTTPS traffic routed through Caddy.
- Keep PostgreSQL, Prosody internals, Jitsi internals, Docker, and host administration off public DNS.
- Keep local, staging, and production domains separate.
- Support automatic TLS certificate handling through the reverse proxy.
- Avoid committing real domains, TLS private keys, certificate data, or DNS provider secrets.
- Keep public registration disabled.
- Keep open federation disabled unless a later reviewed policy enables it.
- Keep Jitsi room creation authenticated and role-gated.

DNS must support the trust model. A working hostname must not bypass portal roles, room policy, meeting policy, suspension state, or audit rules.

## 2. Root Domain vs Subdomain Model

Orthodox Connect should use one operator-controlled root domain with service-specific subdomains.

Model:

```text
ROOT_DOMAIN
PORTAL_DOMAIN
CHAT_DOMAIN
MEET_DOMAIN
LIBRARY_DOMAIN
```

The root domain is the administrative base. Service subdomains are the public entrypoints users actually visit.

Rules:

- Do not hard-code real domains in repository files.
- Do not use production domains in local development.
- Do not use staging domains for production users.
- Keep each environment on its own hostname set.
- Use explicit subdomains instead of relying on one route to serve every service.
- Do not publish service hostnames before the service is reviewed and routed intentionally.

The root domain may show a simple landing or redirect later, but the current service model depends on explicit service hostnames.

## 3. Service Subdomains

Public service hostnames should stay predictable and limited.

| Service          | Environment Variable | Public Use                         | Current Status |
| ---------------- | -------------------- | ---------------------------------- | -------------- |
| portal           | `PORTAL_DOMAIN`      | Portal and admin workflows          | Current        |
| chat             | `CHAT_DOMAIN`        | Converse.js and XMPP browser paths  | Current        |
| meet             | `MEET_DOMAIN`        | Jitsi Meet web access               | Current        |
| library          | `LIBRARY_DOMAIN`     | PDF and ebook library access        | Future         |
| admin/internal   | None                 | Internal service control            | Not public     |

Portal hostname rules:

- Routes to the portal service through Caddy.
- Hosts invite, verification, room, meeting, and admin workflows.
- Admin pages must remain role-gated.

Chat hostname rules:

- Routes the web chat frontend through Caddy.
- Routes XMPP WebSocket and BOSH browser paths to Prosody through Caddy.
- Must not publish native Prosody ports by default.

Meet hostname rules:

- Routes Jitsi web traffic through Caddy.
- Keeps Jitsi room creation authenticated.
- Does not expose Jitsi internal Prosody, Jicofo, or control services.

Library hostname rules:

- Remains a placeholder until a library service is implemented.
- Must not expose anonymous library access.
- Must not expose uploaded files before library access policy exists.

Admin and internal hostname rules:

- Do not create public admin or internal service hostnames for MVP.
- Use Docker service names and private Docker networks for internal upstream routing.
- Host, Docker, database, Prosody admin, and Jitsi internal control access must stay outside public DNS.

## 4. Internal vs External DNS Considerations

External DNS is for public browser access. Internal service discovery is handled by Docker networks.

External DNS should point only to public entrypoints:

- Portal.
- Chat.
- Meetings.
- Library placeholder only after review.

Internal service names should stay inside Docker:

- `portal`
- `postgres`
- `prosody`
- `converse`
- `jitsi-web`
- `jitsi-prosody`
- `jitsi-jicofo`
- `jitsi-jvb`
- `reverse-proxy`

Rules:

- Do not create public DNS records for PostgreSQL.
- Do not create public DNS records for Prosody admin interfaces.
- Do not create public DNS records for Jitsi internal components.
- Do not create public DNS records for Docker or host administration.
- Do not rely on public DNS for container-to-container routing.
- Keep internal upstreams in Caddy pointed at Docker service names, not host ports.

Split-horizon DNS may be useful for some operators, but it is not required by the current MVP. If used later, it must not route users around Caddy or around portal policy.

## 5. Local Development Hostnames

Local development should use fake, disposable hostnames.

Recommended shape:

```text
ROOT_DOMAIN=orthodox-connect.localhost
PORTAL_DOMAIN=portal.orthodox-connect.localhost
CHAT_DOMAIN=chat.orthodox-connect.localhost
MEET_DOMAIN=meet.orthodox-connect.localhost
LIBRARY_DOMAIN=library.orthodox-connect.localhost
```

Local development rules:

- Use fake data only.
- Use local or disposable secrets only.
- Do not use production domains.
- Do not request public certificates for casual local work.
- Do not copy production `.env` values into local development.
- Keep local hostnames documented as setup examples, not production guidance.

If a browser, operating system, or local network does not resolve the chosen local names, the operator may add local host mappings outside this repository.

## 6. TLS Certificate Strategy

Caddy is the certificate handling layer for public HTTP and HTTPS routes.

Production strategy:

- Use real operator-controlled DNS names.
- Point public DNS records at the deployment host before certificate issuance.
- Allow Caddy to obtain and renew certificates automatically.
- Keep ports `80/tcp` and `443/tcp` reachable for normal ACME HTTP and HTTPS operation where the deployment uses that model.
- Set `ACME_EMAIL` or equivalent operator contact value where supported.

Rules:

- Do not commit TLS certificates.
- Do not commit TLS private keys.
- Do not manually add certificate files to the repository.
- Treat Caddy data volumes as sensitive because they may contain ACME account and certificate material.
- Review DNS and public ports before troubleshooting certificate failures.

Local development may use local HTTP, browser exceptions, or local-only certificates where needed. Local certificate choices must not be documented as production TLS.

## 7. Reverse Proxy Integration

Caddy is the public HTTP and HTTPS entrypoint.

Current routing model:

| Hostname Variable | Public Purpose                 | Internal Upstream |
| ----------------- | ------------------------------ | ----------------- |
| `PORTAL_DOMAIN`   | Portal and admin workflows      | `portal:8000`     |
| `CHAT_DOMAIN`     | Converse.js frontend            | `converse:80`     |
| `CHAT_DOMAIN`     | XMPP WebSocket and BOSH paths   | `prosody:5280`    |
| `MEET_DOMAIN`     | Jitsi Meet web interface        | `jitsi-web:80`    |
| `LIBRARY_DOMAIN`  | Future library placeholder      | Placeholder       |

Reverse proxy rules:

- Route by hostname and path.
- Preserve WebSocket upgrades for chat and Jitsi.
- Keep internal services off public host ports unless a reviewed deployment requires otherwise.
- Avoid logging sensitive query strings.
- Apply security headers where compatible with each service.
- Fail closed when an upstream is missing or unhealthy.

DNS changes should be coordinated with Caddy routing changes, but this document does not modify the Caddyfile.

## 8. Tor and Onion Hostname Placeholder

Tor onion access is future scope.

Placeholder model:

- Onion hostnames are separate from DNS hostnames.
- Onion routes should be limited to portal and chat unless a later review approves more.
- Jitsi media should not be promised over onion access.
- PostgreSQL, Docker, Prosody admin, Jitsi internals, and host administration must not have onion endpoints.
- Onion private keys must be treated as secrets.

Rules:

- Do not add onion hostnames to repository files before implementation.
- Do not commit onion private keys.
- Do not use onion access to bypass portal authentication, admin roles, verification, room access, meeting policy, or audit records.
- Document onion hostname distribution only after the Tor implementation is reviewed.

Onion access is a separate access path to the same trust model, not a separate community identity system.

## 9. DNS Failure Scenarios

DNS failure can make healthy services unreachable.

Common scenarios:

| Scenario                      | Effect                                  | Response |
| ----------------------------- | --------------------------------------- | -------- |
| Missing `A` or `AAAA` record  | Hostname does not resolve               | Restore the intended record. |
| Wrong target address          | Traffic reaches the wrong host          | Correct the record and review exposure. |
| Stale cached record           | Some users reach old infrastructure     | Wait for TTL and avoid unsafe temporary fixes. |
| Registrar outage              | Domains cannot be changed               | Use offline operator contacts and wait or migrate only by reviewed plan. |
| DNS provider outage           | Hostnames fail or cannot be edited      | Confirm provider status and avoid unreviewed alternate domains. |
| Certificate renewal failure   | HTTPS warnings or route failure         | Check DNS, public ports, and Caddy logs. |
| Domain takeover or compromise | Impersonation or traffic capture risk   | Disable affected routes, rotate secrets, and notify through approved channels. |

DNS failure response:

1. Confirm whether failure is DNS, reverse proxy, host, or certificate related.
2. Check registrar and DNS provider status.
3. Confirm portal, chat, meet, and root records.
4. Avoid IP-only public user guidance.
5. Avoid temporary public domains unless TLS, trust, and user communication are reviewed.
6. Preserve logs and operator notes.
7. Recheck Caddy certificate state after DNS is restored.

## 10. Migration Between Domains

Domain migration should be planned as a production change.

Migration steps:

1. Select the new operator-controlled root domain and service subdomains.
2. Add new environment values in the target environment.
3. Prepare DNS records with an appropriate TTL.
4. Confirm Caddy routing will match the new hostnames.
5. Confirm Jitsi public URL and JWT links use the new meeting hostname.
6. Confirm Converse.js WebSocket and BOSH URLs use the new chat hostname.
7. Confirm portal links use the new portal hostname.
8. Back up PostgreSQL, Prosody data, Jitsi config, reverse proxy data, and `.env` through operator storage.
9. Deploy the new configuration in staging where practical.
10. Switch production DNS only after validation.
11. Keep old hostnames available briefly only if they route to the same reviewed services and do not weaken security.
12. Remove old hostnames when users have moved.

Migration rules:

- Do not reuse production secrets in staging.
- Do not publish new domains before TLS is ready.
- Do not leave abandoned hostnames pointing to stale infrastructure.
- Do not create redirects that expose invite tokens, recovery tokens, JWT bodies, or private route data.
- Record the migration in operator notes.

Federation, Tor, library, and bridge features need separate review before domain migration includes them.

## 11. Privacy Considerations

DNS and TLS metadata can reveal service structure.

Privacy risks:

- Public DNS records reveal portal, chat, meeting, and future library hostnames.
- Certificate transparency logs may reveal public TLS hostnames.
- Hostnames can reveal community identity, location, or service purpose.
- Reverse proxy logs may connect hostnames, paths, IP addresses, user agents, and timestamps.
- Meeting and room names can leak if placed into URLs or logs.
- Backup manifests may reveal hostnames or deployment layout.

Privacy rules:

- Use hostnames that are clear enough for users but avoid unnecessary sensitive details.
- Avoid putting private room names, clergy-only labels, youth labels, or pastoral details in hostnames.
- Keep logs short-lived unless policy requires longer retention.
- Avoid logging sensitive query strings.
- Treat Caddy data, DNS provider credentials, `.env`, and backups as sensitive.
- Do not publish staging hostnames to ordinary users.
- Do not include real domains in repository examples.

Operators should assume public DNS records are visible to outsiders.

## 12. Rollback Plan

DNS rollback should restore the last known-good public route without deleting service data.

Rollback steps:

1. Identify the affected hostname, record, certificate, route, or provider setting.
2. Preserve current DNS values and relevant logs for review.
3. Restore the last known-good DNS records.
4. Restore the previous `.env` hostname values only if the deployment configuration changed.
5. Confirm Caddy routes match the restored hostnames.
6. Confirm certificates are valid or reissued by Caddy.
7. Confirm portal, chat, XMPP browser transports, and Jitsi routes load.
8. Confirm public registration remains disabled.
9. Confirm open federation remains disabled.
10. Confirm Jitsi authentication remains enabled.
11. Confirm internal service ports remain private.
12. Rotate secrets if traffic may have reached untrusted infrastructure.
13. Notify users through an approved communication path after administrator review.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, reverse proxy data, backups, or unrelated service configuration.
