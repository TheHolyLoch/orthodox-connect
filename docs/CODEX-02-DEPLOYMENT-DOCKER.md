# Orthodox Connect Docker Deployment Plan

## Current Directory Tree

```text
orthodox-connect/
	.env
	.env.example
	.gitignore
	docs/
		CODEX-00-PROJECT-BRIEF.md
		CODEX-01-ARCHITECTURE.md
		CODEX-02-DEPLOYMENT-DOCKER.md
		CODEX-03-IDENTITY-VERIFICATION.md
		CODEX-04-SECURITY-MODEL.md
		CODEX-05-MVP-PASSES.md
	converse/
	jitsi/
	portal/
		app/
		migrations/
	prosody/
	reverse-proxy/
	scripts/
	backups/
```

Runtime-only files such as `.env`, backups, generated volumes, logs, and caches must stay out of Git.

## Docker Compose Services

| Service              | MVP Status | Role                                                                                                      |
| -------------------- | ---------- | --------------------------------------------------------------------------------------------------------- |
| reverse-proxy        | Required   | Public entrypoint for HTTPS, WebSocket routing, TLS, and service routing.                                  |
| portal               | Required   | Admin interface for invitations, verification, roles, room policy, and account lifecycle actions.          |
| postgres             | Required   | Persistent portal state, invitations, verification records, role assignments, and audit records.           |
| prosody              | Required   | XMPP server for accounts, direct messaging, MUC rooms, and XMPP access control.                            |
| converse             | Required   | Static web chat frontend served through the reverse proxy.                                                 |
| jitsi-web            | Required   | Browser-facing Jitsi Meet web interface.                                                                  |
| jitsi-prosody        | Required   | Jitsi XMPP component for meeting control and authentication support.                                       |
| jitsi-jicofo         | Required   | Jitsi conference focus service.                                                                           |
| jitsi-jvb            | Required   | Jitsi video bridge for media transport.                                                                   |
| redis                | Optional   | Only use if portal sessions, rate limits, queues, or locks need a runtime store outside PostgreSQL.        |
| kavita               | Later      | Library service for PDF and ebook access.                                                                 |
| tor                  | Later      | Onion service entrypoint after normal HTTPS deployment is stable.                                          |

## Networks

| Network  | Services                                            | Purpose                                                     |
| -------- | --------------------------------------------------- | ----------------------------------------------------------- |
| public   | reverse-proxy, jitsi-jvb                            | Services that need host-published public ports.             |
| internal | reverse-proxy, portal, postgres, prosody, converse   | Internal HTTP, database, and application traffic.           |
| xmpp     | reverse-proxy, prosody, converse                     | Internal XMPP browser transport traffic.                    |
| video    | reverse-proxy, jitsi-web, jitsi-prosody, Jitsi stack | Internal Jitsi traffic plus JVB attachment to public media. |

Default policy should avoid exposing internal service ports to the host unless required.

## Volumes

| Volume                    | Service       | Contents                        | Backup |
| ------------------------- | ------------- | ------------------------------- | ------ |
| postgres_data             | postgres      | Portal database files.          | Yes    |
| prosody_data              | prosody       | Prosody data.                   | Yes    |
| reverse_proxy_data        | reverse-proxy | Caddy ACME and runtime data.    | Yes    |
| reverse_proxy_config      | reverse-proxy | Caddy runtime config.           | Yes    |
| jitsi_web_config          | jitsi-web     | Generated Jitsi web config.     | Yes    |
| jitsi_prosody_config      | jitsi-prosody | Generated Jitsi Prosody config. | Yes    |
| jitsi_jicofo_config       | jitsi-jicofo  | Generated Jicofo config.        | Yes    |
| jitsi_jvb_config          | jitsi-jvb     | Generated JVB config.           | Yes    |

## Secrets and .env Variables

The deployment should use `.env` for local operator settings and Docker secrets or mounted secret files for high-value secrets where practical.

Current `.env` values:

| Variable                      | Required | Purpose                                      |
| ----------------------------- | -------- | -------------------------------------------- |
| ROOT_DOMAIN                   | Yes      | Parent instance domain.                      |
| PORTAL_DOMAIN                 | Yes      | Portal hostname.                             |
| CHAT_DOMAIN                   | Yes      | Chat hostname.                               |
| MEET_DOMAIN                   | Yes      | Jitsi hostname.                              |
| LIBRARY_DOMAIN                | Yes      | Reserved library hostname.                   |
| XMPP_DOMAIN                   | Yes      | Prosody XMPP domain.                         |
| XMPP_ADMIN_JID                | Yes      | Prosody admin JID.                           |
| XMPP_MUC_DOMAIN               | Yes      | Prosody MUC domain.                          |
| XMPP_UPLOAD_DOMAIN            | Planned  | Reserved upload component domain.            |
| XMPP_REGISTRATION_ENABLED     | Yes      | Must stay `false`.                           |
| CONVERSE_BOSH_URL             | Yes      | BOSH URL through Caddy.                      |
| CONVERSE_WEBSOCKET_URL        | Yes      | XMPP WebSocket URL through Caddy.            |
| POSTGRES_DB                   | Yes      | Portal database name.                        |
| POSTGRES_USER                 | Yes      | Portal database user.                        |
| POSTGRES_PASSWORD             | Yes      | Portal database password.                    |
| PORTAL_DATABASE_URL           | Yes      | Portal PostgreSQL URL.                       |
| PORTAL_ADMIN_HOST             | Yes      | Admin UI bind host when run from the repo.   |
| PORTAL_ADMIN_PORT             | Yes      | Admin UI port when run from the repo.        |
| PORTAL_INVITE_TOKEN_BYTES     | Yes      | Invite token entropy size.                   |
| PORTAL_SECRET_KEY             | Yes      | Portal signing secret.                       |
| JITSI_PUBLIC_URL              | Yes      | Public Jitsi URL.                            |
| JITSI_ENABLE_AUTH             | Yes      | Must stay `1`.                               |
| JITSI_ENABLE_GUESTS           | Yes      | Must stay `0` for MVP.                       |
| JITSI_JWT_APP_ID              | Yes      | Jitsi JWT app ID.                            |
| JITSI_JWT_APP_SECRET          | Yes      | Jitsi JWT shared secret.                     |
| JITSI_MEETING_CREATOR_ROLES   | Yes      | Roles allowed to create meetings.            |
| JITSI_TOKEN_TTL_SECONDS       | Yes      | Default meeting token lifetime.              |
| JITSI_JICOFO_AUTH_PASSWORD    | Yes      | Jitsi internal Jicofo password.              |
| JITSI_JVB_AUTH_PASSWORD       | Yes      | Jitsi internal JVB password.                 |
| ACME_EMAIL                    | Prod     | Caddy ACME email.                            |
| BACKUP_ROOT                   | Yes      | Local backup output directory.               |
| RESTORE_CONFIRM               | Restore  | Restore safety confirmation.                 |

`.env.example` contains placeholders only. Real secrets belong only in local `.env` or operator-managed secret storage.

## Reverse Proxy Routing

Routing should support domain-based deployment first. Path-based deployment can be considered later if required.

| Public Route               | Backend Service | Notes                                                                  |
| -------------------------- | --------------- | ---------------------------------------------------------------------- |
| `https://portal.example`    | portal          | Admin and verification workflow.                                       |
| `https://chat.example`      | converse        | Browser chat frontend.                                                 |
| `https://xmpp.example`      | prosody         | XMPP WebSocket, BOSH, and related browser-accessible XMPP endpoints.   |
| `https://meet.example`      | jitsi-web       | Jitsi Meet web interface.                                              |
| `https://library.example`   | kavita          | Later library access only.                                             |

The reverse proxy should:

- Terminate TLS.
- Preserve WebSocket upgrades.
- Route XMPP browser transports to Prosody.
- Route Jitsi web traffic and required WebSocket paths correctly.
- Keep internal admin or service endpoints private.
- Redirect HTTP to HTTPS in production.

Caddy is the reverse proxy.

## Ports

| Port      | Exposure | Service              | Purpose                                                           |
| --------- | -------- | -------------------- | ----------------------------------------------------------------- |
| 80/tcp    | Public   | reverse-proxy        | HTTP redirect and ACME HTTP challenge if used.                    |
| 443/tcp   | Public   | reverse-proxy        | HTTPS for portal, chat, XMPP browser transport, and Jitsi web.    |
| 5222/tcp  | Optional | prosody              | Native XMPP client connections.                                   |
| 5269/tcp  | Optional | prosody              | XMPP federation, disabled by default for MVP.                     |
| 5280/tcp  | Internal | prosody              | BOSH or WebSocket if routed only through reverse proxy.           |
| 5432/tcp  | Internal | postgres             | Portal database.                                                  |
| 6379/tcp  | Internal | redis                | Optional Redis runtime store.                                     |
| 10000/udp | Public   | jitsi-jvb            | Jitsi media traffic.                                              |
| 4443/tcp  | Optional | jitsi-jvb            | Jitsi TCP fallback if enabled.                                    |

Production should publish only the ports required for the selected deployment.

## Backup Targets

Backups must include:

- PostgreSQL logical dumps for portal state.
- Prosody data and room state.
- Prosody configuration.
- Reverse proxy TLS certificate data, if managed by the stack.
- Jitsi configuration and generated secrets.
- Portal uploaded files, if uploads are added.
- Kavita metadata and library files in the later library phase.
- `.env` and secret material through a secure operator-controlled backup path, not Git.

Backups should not include:

- Container images.
- Build caches.
- Temporary logs unless required for incident review.
- Redis data unless Redis is intentionally used for persistent jobs.

## Development Deployment

Development deployment should favor local iteration and clear separation from production data.

Expected traits:

- Local domain names or localhost ports.
- Self-signed certificates or local TLS helper if browser features require HTTPS.
- Test-only `.env` values.
- Disposable PostgreSQL and Prosody volumes unless testing migrations or backup restore.
- Optional Jitsi disablement if the task does not involve video.
- Verbose logging.
- No public federation.
- No real parish data.
- No real invitation email unless explicitly testing mail delivery.

Development may use `.localhost` domains from `.env.example`. Real Let's Encrypt certificates require real public DNS names.

## Production Deployment

Production deployment should favor a small, auditable public surface.

Expected traits:

- Public DNS for selected domains.
- Valid TLS certificates.
- Published ports limited to required public services.
- PostgreSQL and internal service ports kept private.
- Persistent named volumes or explicit host paths.
- Regular tested backups.
- Strong secrets generated outside Git.
- Admin accounts limited to trusted operators.
- Federation disabled by default.
- Monitoring and log review appropriate for the operator.
- Upgrade process tested against a backup before production use.

Production should not depend on manual container shell edits. Configuration should be reproducible from committed templates plus operator-owned secrets.

## What Must Not Be Committed to Git

- `.env`
- Real passwords, tokens, API keys, or shared secrets.
- TLS private keys, ACME account keys, or certificate stores.
- PostgreSQL data directories or dumps containing real data.
- Prosody user data, room state, or private keys.
- Jitsi generated secrets or private configuration.
- Portal upload data containing private files.
- Kavita library files or metadata containing private library state.
- Backups.
- Logs containing usernames, IP addresses, message metadata, invite links, or administrative actions.
- Local development database files.
- Any file copied from a production server unless it has been reviewed and scrubbed.
