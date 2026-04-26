# Orthodox Connect

Orthodox Connect is a self-hosted communications stack for Orthodox parishes, clergy, monastics, and laity. It combines a Caddy reverse proxy, Prosody XMPP, Converse.js web chat, Jitsi Meet, PostgreSQL, and a small portal for invites, verification, rooms, meetings, audit records, and local backups.

The MVP is invite-only. Public registration and open XMPP federation are disabled by default.

## Table of Contents

- [Status](#status)
- [Requirements](#requirements)
- [Real Host Setup](#real-host-setup)
- [Configure](#configure)
- [Environment Variables](#environment-variables)
- [Certificates](#certificates)
- [Run](#run)
- [Portal Tools](#portal-tools)
- [Admin UI](#admin-ui)
- [Chat and Meetings](#chat-and-meetings)
- [Backups](#backups)
- [Security Notes](#security-notes)

## Status

Implemented so far:

- Docker Compose services for Caddy, PostgreSQL, Prosody, Converse.js, and Jitsi.
- Caddy routes for portal, chat, Jitsi, and a disabled library placeholder.
- Prosody config with registration disabled and federation disabled for MVP.
- Converse.js web chat pointed at Prosody browser transports.
- Portal database migrations for users, groups, roles, invites, verification, rooms, meetings, and audit events.
- Portal CLI workflows for invites, verification, room access, meeting tokens, and migrations.
- Minimal admin UI for viewing portal state and managing invites and verification.
- Local backup and restore scripts for PostgreSQL and service volumes.

Still rough:

- The portal is not packaged as a production image yet. Run portal CLI/admin commands from the repo on the host.
- No public signup flow exists. Users are created by invite redemption and then manually approved.
- Real deployment needs real secrets in `.env`, DNS, and firewall rules.

## Requirements

- Linux host or VPS.
- Docker Engine and Docker Compose plugin.
- Python 3.11 or newer for local portal tools.
- Public DNS records for real HTTPS deployment.

Recommended starting host:

- 2 CPU cores.
- 4 GB RAM minimum, more if using Jitsi often.
- 40 GB disk minimum.

## Real Host Setup

Create DNS records before starting Caddy. Use normal `A` or `AAAA` records pointing at the host.

| Name      | Example                      | Purpose        |
| --------- | ---------------------------- | -------------- |
| Portal    | `portal.example.org`         | Admin portal   |
| Chat      | `chat.example.org`           | Web chat       |
| Meet      | `meet.example.org`           | Jitsi Meet     |
| Library   | `library.example.org`        | Disabled stub  |

Open these ports on the host firewall or provider firewall:

| Port        | Purpose                      |
| ----------- | ---------------------------- |
| `80/tcp`    | HTTP and Let's Encrypt checks |
| `443/tcp`   | HTTPS                         |
| `10000/udp` | Jitsi media                   |

Clone the repo:

```bash
git clone https://example.org/orthodox-connect.git
cd orthodox-connect
```

## Configure

Create a local `.env`:

```bash
cp .env.example .env
```

Edit `.env` for your host:

```bash
ROOT_DOMAIN=example.org
PORTAL_DOMAIN=portal.example.org
CHAT_DOMAIN=chat.example.org
MEET_DOMAIN=meet.example.org
LIBRARY_DOMAIN=library.example.org

CONVERSE_BOSH_URL=https://chat.example.org/http-bind
CONVERSE_WEBSOCKET_URL=wss://chat.example.org/xmpp-websocket

POSTGRES_PASSWORD=replace_with_a_real_password
PORTAL_SECRET_KEY=replace_with_a_real_secret
JITSI_JWT_APP_SECRET=replace_with_a_real_secret
JITSI_JICOFO_AUTH_PASSWORD=replace_with_a_real_password
JITSI_JVB_AUTH_PASSWORD=replace_with_a_real_password

ACME_EMAIL=admin@example.org
```

Generate local secrets on your workstation or server:

```bash
openssl rand -hex 32
```

Do not commit `.env`.

## Environment Variables

| Variable                      | Required | Purpose                                      |
| ----------------------------- | -------- | -------------------------------------------- |
| `ROOT_DOMAIN`                 | Yes      | Parent domain for the instance.              |
| `PORTAL_DOMAIN`               | Yes      | Public portal hostname.                      |
| `CHAT_DOMAIN`                 | Yes      | Public chat hostname.                        |
| `MEET_DOMAIN`                 | Yes      | Public Jitsi hostname.                       |
| `LIBRARY_DOMAIN`              | Yes      | Reserved library hostname.                   |
| `XMPP_DOMAIN`                 | Yes      | Prosody local XMPP domain.                   |
| `XMPP_ADMIN_JID`              | Yes      | Prosody admin JID placeholder.               |
| `XMPP_MUC_DOMAIN`             | Yes      | Prosody group chat domain.                   |
| `XMPP_REGISTRATION_ENABLED`   | Yes      | Must stay `false` for the MVP.               |
| `CONVERSE_BOSH_URL`           | Yes      | Browser BOSH URL routed through Caddy.       |
| `CONVERSE_WEBSOCKET_URL`      | Yes      | Browser XMPP WebSocket URL through Caddy.    |
| `POSTGRES_DB`                 | Yes      | Portal database name.                        |
| `POSTGRES_USER`               | Yes      | Portal database user.                        |
| `POSTGRES_PASSWORD`           | Yes      | Portal database password.                    |
| `PORTAL_DATABASE_URL`         | Yes      | PostgreSQL URL used by portal tools.         |
| `PORTAL_SECRET_KEY`           | Yes      | Portal signing secret placeholder.           |
| `JITSI_PUBLIC_URL`            | Yes      | Public Jitsi URL.                            |
| `JITSI_ENABLE_AUTH`           | Yes      | Keep `1` to require Jitsi authentication.    |
| `JITSI_ENABLE_GUESTS`         | Yes      | Keep `0` for no anonymous public guests.     |
| `JITSI_JWT_APP_ID`            | Yes      | Jitsi JWT app identifier.                    |
| `JITSI_JWT_APP_SECRET`        | Yes      | Jitsi JWT shared secret.                     |
| `JITSI_JICOFO_AUTH_PASSWORD`  | Yes      | Jitsi internal Jicofo password.              |
| `JITSI_JVB_AUTH_PASSWORD`     | Yes      | Jitsi internal JVB password.                 |
| `ACME_EMAIL`                  | Prod     | Email used by Caddy for Let's Encrypt.       |
| `BACKUP_ROOT`                 | Yes      | Local backup output path.                    |
| `RESTORE_CONFIRM`             | Restore  | Must be `restore-local-backup` for restores. |

## Certificates

Caddy handles certificates automatically through Let's Encrypt. You do not need to create or mount TLS certificates manually.

For Let's Encrypt to work:

- DNS must point to the host.
- Ports `80/tcp` and `443/tcp` must reach the Caddy container.
- `ACME_EMAIL` should be set in `.env`.
- `PORTAL_DOMAIN`, `CHAT_DOMAIN`, `MEET_DOMAIN`, and `LIBRARY_DOMAIN` must be real names, not `.localhost` names.

Start Caddy with the stack. On first public start, Caddy requests certificates and stores ACME data in the `reverse_proxy_data` and `reverse_proxy_config` Docker volumes.

For local-only testing, keep the `.localhost` domains in `.env.example`. Browsers may warn or fail on HTTPS because public Let's Encrypt certificates are not issued for `.localhost`.

## Run

Check the Compose file:

```bash
docker compose --env-file .env config
```

Start the stack:

```bash
docker compose --env-file .env up -d
```

Check service status:

```bash
docker compose --env-file .env ps
```

View logs:

```bash
docker compose --env-file .env logs -f reverse-proxy
docker compose --env-file .env logs -f prosody
docker compose --env-file .env logs -f jitsi-web
```

Stop the stack:

```bash
docker compose --env-file .env stop
```

## Portal Tools

Create a Python environment for portal CLI/admin use:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r portal/requirements.txt
```

Load `.env` and point Python at the repo:

```bash
set -a
. .env
set +a
export PYTHONPATH="$PWD"
```

Run migrations:

```bash
python3 -m portal.app.cli migrate
```

Create an invite:

```bash
python3 -m portal.app.cli create-invite \
	--created-by-user-id ADMIN_USER_UUID \
	--ttl-hours 168
```

Redeem an invite:

```bash
python3 -m portal.app.cli redeem-invite \
	--token INVITE_TOKEN \
	--display-name "User Name" \
	--email user@example.org
```

List pending verification requests:

```bash
python3 -m portal.app.cli list-verifications --status pending
```

Approve a verification request:

```bash
python3 -m portal.app.cli approve-verification \
	--admin-user-id ADMIN_USER_UUID \
	--request-id REQUEST_UUID
```

Reject a verification request:

```bash
python3 -m portal.app.cli reject-verification \
	--admin-user-id ADMIN_USER_UUID \
	--request-id REQUEST_UUID \
	--reason "Reason"
```

## Admin UI

Start the minimal admin UI from the repo:

```bash
python3 -m portal.app.admin
```

Open:

```text
http://127.0.0.1:8000/admin
```

The admin UI asks for an acting admin user ID. The user must be approved and have an admin role such as `parish_admin`, `diocesan_admin`, or `platform_admin`.

The UI can view:

- Users.
- Groups and parishes.
- Roles.
- Invites.
- Verification requests.
- Rooms and channels.
- Audit events.

The UI can:

- Create invites.
- Revoke unused invites.
- Approve verification requests.
- Reject verification requests.

## Chat and Meetings

Open chat at:

```text
https://chat.example.org
```

Open Jitsi at:

```text
https://meet.example.org
```

Jitsi uses JWT authentication. Meeting links and tokens should be issued through portal meeting commands for approved users or explicitly allowed guests.

Create a meeting:

```bash
python3 -m portal.app.cli create-meeting \
	--actor-user-id ADMIN_USER_UUID \
	--name "Parish Meeting" \
	--slug parish-meeting \
	--room-id ROOM_UUID \
	--allow-guests
```

Issue a user meeting token:

```bash
python3 -m portal.app.cli issue-meeting-user-token \
	--meeting-id MEETING_UUID \
	--user-id USER_UUID
```

## Backups

Backups are local filesystem backups. Remote backup providers are not configured.

Create a backup:

```bash
scripts/backup.sh
```

List backups:

```bash
scripts/list-backups.sh
```

Restore from a backup:

```bash
RESTORE_CONFIRM=restore-local-backup scripts/restore.sh backups/20260101T000000Z
```

Backups are written under `BACKUP_ROOT`, which defaults to `./backups`. The `backups/` directory is ignored by Git.

Backups include:

- PostgreSQL logical dump.
- Prosody data volume and checked-in Prosody config.
- Jitsi config volumes and checked-in Jitsi config.
- Reverse proxy Caddy data/config volumes.
- Portal migrations.

## Security Notes

- Public registration is disabled.
- XMPP federation is disabled for MVP.
- Do not commit `.env`, backup output, real secrets, certificates, keys, or production data.
- Admin and verification actions are audited in PostgreSQL.
- Backups contain sensitive account and access metadata. Store them as private operator data.
- The MVP does not claim end-to-end encryption.
