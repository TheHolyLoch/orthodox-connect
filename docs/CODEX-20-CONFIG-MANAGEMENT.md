# Orthodox Connect Configuration Management

## 1. Configuration Goals

Orthodox Connect configuration must be explicit, reviewable, and separated from application code.

Goals:

- Keep secrets out of Git.
- Keep local, staging, and production settings separate.
- Use environment variables for deploy-time configuration.
- Make required settings visible in `.env.example`.
- Avoid real domains, real users, real passwords, and real tokens in documentation.
- Keep public registration disabled unless a later approved stage changes that policy.
- Keep open federation disabled unless trusted federation is deliberately enabled later.
- Make restore and rollback work without guessing which settings were active.

Configuration should support small parish deployments while still leaving room for diocesan or federated deployments later.

## 2. Environment Variable Strategy

Environment variables are the project default for runtime configuration.

Configuration should follow these rules:

- `.env.example` lists every required variable with placeholder values.
- `.env` stores local operator values and must not be committed.
- Docker Compose reads values from `.env` or the shell environment.
- Services should use internal Docker service names for upstreams.
- Public hostnames should come from variables, not hard-coded domains.
- Secrets should be passed as variables, never embedded in config files.
- Optional features should have explicit disabled defaults.

Important variable groups:

| Group          | Examples                                                                 | Purpose                                  |
| -------------- | ------------------------------------------------------------------------ | ---------------------------------------- |
| Domains        | `ROOT_DOMAIN`, `PORTAL_DOMAIN`, `CHAT_DOMAIN`, `MEET_DOMAIN`             | Public hostnames for reverse proxy routes |
| XMPP           | `XMPP_DOMAIN`, `XMPP_ADMIN_JID`, `XMPP_MUC_DOMAIN`                       | Prosody virtual hosts and components      |
| Converse       | `CONVERSE_BOSH_URL`, `CONVERSE_WEBSOCKET_URL`                            | Browser chat connection endpoints         |
| PostgreSQL     | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`                      | Database service settings                 |
| Portal         | `PORTAL_DATABASE_URL`, `PORTAL_SECRET_KEY`, `PORTAL_INVITE_TOKEN_BYTES`   | Portal runtime and token settings         |
| Jitsi          | `JITSI_PUBLIC_URL`, `JITSI_JWT_APP_ID`, `JITSI_JWT_APP_SECRET`           | Meeting authentication and links          |
| Backups        | `BACKUP_ROOT`, `RESTORE_CONFIRM`                                         | Local backup and restore controls         |

## 3. `.env` vs System Environment Usage

`.env` is the recommended local development and simple host deployment method.

Use `.env` when:

- Running Docker Compose directly.
- Testing on a single host.
- Preparing a staging host with non-production data.
- Keeping setup simple for a parish or small community administrator.

Use system environment variables when:

- A host already manages service environment separately.
- Operators need stricter file permissions outside the repository.
- Deployment tooling injects variables at runtime.
- Production policy keeps secrets outside the application directory.

Rules:

- `.env.example` is committed.
- `.env` is not committed.
- Production `.env` files must not be copied into development or staging.
- Staging must use staging-only secrets.
- Shell-provided environment variables may override `.env` values where Docker Compose or scripts support that behavior.
- Documentation should show placeholder values only.

## 4. Required vs Optional Variables

Required variables are needed for a normal MVP deployment. Optional variables are for planned or environment-specific behavior.

| Variable                         | Status      | Notes                                                   |
| -------------------------------- | ----------- | ------------------------------------------------------- |
| `ROOT_DOMAIN`                    | Required    | Base domain used to derive public service hostnames      |
| `PORTAL_DOMAIN`                  | Required    | Portal hostname                                         |
| `CHAT_DOMAIN`                    | Required    | Converse.js web chat hostname                           |
| `MEET_DOMAIN`                    | Required    | Jitsi Meet hostname                                     |
| `LIBRARY_DOMAIN`                 | Optional    | Placeholder until the library service is implemented     |
| `ACME_EMAIL`                     | Production  | Contact address for automated certificate issuance       |
| `POSTGRES_DB`                    | Required    | Portal database name                                    |
| `POSTGRES_USER`                  | Required    | Portal database user                                    |
| `POSTGRES_PASSWORD`              | Required    | Database password                                       |
| `PORTAL_DATABASE_URL`            | Required    | Portal database connection string                       |
| `PORTAL_SECRET_KEY`              | Required    | Portal session and signing secret                       |
| `PORTAL_INVITE_TOKEN_BYTES`      | Required    | Invite token length control                             |
| `XMPP_DOMAIN`                    | Required    | Main XMPP domain                                        |
| `XMPP_ADMIN_JID`                 | Required    | Administrative JID value                                |
| `XMPP_MUC_DOMAIN`                | Required    | Group chat component domain                             |
| `XMPP_UPLOAD_DOMAIN`             | Optional    | Planned upload component domain                         |
| `XMPP_REGISTRATION_ENABLED`      | Required    | Must remain `false` for MVP                             |
| `CONVERSE_BOSH_URL`              | Required    | Browser BOSH endpoint                                   |
| `CONVERSE_WEBSOCKET_URL`         | Required    | Browser WebSocket endpoint                              |
| `JITSI_PUBLIC_URL`               | Required    | Public Jitsi URL                                        |
| `JITSI_ENABLE_AUTH`              | Required    | Must remain enabled for MVP                             |
| `JITSI_ENABLE_GUESTS`            | Required    | Must remain disabled unless explicitly changed later     |
| `JITSI_JWT_APP_ID`               | Required    | Jitsi JWT issuer or app id                              |
| `JITSI_JWT_APP_SECRET`           | Required    | Jitsi JWT signing secret                                |
| `JITSI_MEETING_CREATOR_ROLES`    | Required    | Roles allowed to create official meetings                |
| `JITSI_TOKEN_TTL_SECONDS`        | Required    | Meeting token lifetime                                  |
| `JITSI_JICOFO_AUTH_PASSWORD`     | Required    | Internal Jitsi component password                       |
| `JITSI_JVB_AUTH_PASSWORD`        | Required    | Internal Jitsi component password                       |
| `BACKUP_ROOT`                    | Required    | Local backup output path                                |
| `RESTORE_CONFIRM`                | Restore     | Explicit restore safety confirmation                    |

## 5. Secret Categories

### Database

Database secrets include:

- `POSTGRES_PASSWORD`
- Credentials embedded in `PORTAL_DATABASE_URL`
- Database dumps created by backup scripts
- Restore archives that contain database data

Rules:

- Use unique database passwords per environment.
- Do not reuse local or staging database passwords in production.
- Do not log full database URLs when they contain credentials.
- Rotate the database password after suspected exposure.

### XMPP

XMPP secrets and sensitive values include:

- Prosody internal component secrets.
- Administrative JIDs.
- Account credentials created outside this design document.
- Prosody data directories and generated state.

Rules:

- Public registration remains disabled.
- Open federation remains disabled or explicitly restricted.
- Administrative interfaces must not be exposed publicly.
- XMPP account creation must stay controlled by the portal or approved admin workflow.

### Jitsi JWT

Jitsi JWT secrets include:

- `JITSI_JWT_APP_SECRET`
- Internal Jitsi component passwords.
- Issued meeting tokens.
- Any future guest access token values.

Rules:

- Do not commit JWT secrets.
- Keep token lifetimes short enough for meeting use.
- Rotate the JWT secret if tokens are leaked.
- After rotation, existing meeting links that depend on old tokens should stop working.

### Portal Auth

Portal authentication secrets include:

- `PORTAL_SECRET_KEY`
- Invite tokens.
- Future recovery tokens.
- Session cookies.
- Admin credentials created outside this document.

Rules:

- Do not log raw invite, recovery, or session tokens.
- Invite tokens must remain single-use unless explicitly marked reusable.
- Privileged roles must not be self-assigned.
- Admin actions must keep audit records.

### Backup Paths

Backup paths are sensitive operational configuration, even when they are not cryptographic secrets.

Sensitive backup-related values include:

- `BACKUP_ROOT`
- Backup archive names.
- Backup manifests.
- Restore staging directories.
- Local paths that reveal deployment layout.

Rules:

- Keep backup output outside Git.
- Do not expose backup directories through the reverse proxy.
- Restrict filesystem access to backup directories on production hosts.
- Treat backup archives as sensitive because they contain database, Prosody, and Jitsi data.

## 6. Secret Rotation Strategy

Rotation should be deliberate and recorded.

General process:

1. Create the new secret.
2. Update the environment value.
3. Restart only the affected services.
4. Verify the affected workflow.
5. Revoke or remove the old secret.
6. Record the rotation in the admin audit log or operator notes.
7. Create a fresh backup after the rotation succeeds.

Rotation guidance:

| Secret Type             | Rotation Trigger                         | Expected Impact                          |
| ----------------------- | ---------------------------------------- | ---------------------------------------- |
| Database password       | Exposure, staff change, scheduled review | Portal database reconnect required       |
| Portal secret key       | Exposure, host compromise                | Existing sessions may become invalid     |
| Jitsi JWT secret        | Token leak, host compromise              | Existing meeting tokens should fail      |
| Jitsi component secrets | Exposure, container compromise           | Jitsi services need coordinated restart  |
| XMPP component secrets  | Exposure, Prosody compromise             | Prosody components need coordinated restart |
| Backup location         | Storage compromise, host migration       | Backup scripts and restore docs need review |

Do not rotate multiple unrelated secrets at the same time unless responding to a host compromise. Smaller rotations are easier to verify and roll back.

## 7. Secret Storage Rules

Rules:

- Keep `.env` out of Git.
- Keep `.env` readable only by the operator account where possible.
- Do not paste real secrets into docs, issues, commits, chat, or screenshots.
- Do not include `.env` in backup archives unless the backup is explicitly protected.
- Do not commit generated Caddy certificate storage.
- Do not commit Prosody data.
- Do not commit Jitsi generated secrets or runtime state.
- Do not commit database dumps.
- Do not commit backup archives.
- Do not print secrets from scripts unless the command is explicitly for local operator inspection.

`.env.example` should show the shape of the configuration, not real values.

## 8. Development vs Production Config Differences

Local development:

- Uses placeholder domains or local hostnames.
- Uses disposable secrets.
- Uses fake users and fake data only.
- May use local HTTP routes where documented.
- Does not need production certificate issuance.

Staging:

- Uses staging-only domains and secrets.
- Uses fake or scrubbed data.
- Should match production service layout.
- Should test backup and restore before production changes.

Production:

- Uses real operator-controlled domains.
- Uses production-only secrets.
- Uses automated public certificates through the reverse proxy.
- Keeps public registration disabled.
- Keeps open federation disabled until trusted federation is approved.
- Keeps Jitsi room creation authenticated and role-gated.
- Keeps backups on local filesystem storage for the current stage.

Production values must not be copied into local development.

## 9. Validation and Startup Checks

Configuration validation should fail closed.

Startup checks should confirm:

- Required variables are present.
- Required secrets are not blank.
- Placeholder values are not used in production.
- `XMPP_REGISTRATION_ENABLED=false`.
- Jitsi authentication is enabled.
- Anonymous Jitsi room creation is disabled.
- Public hostnames are set.
- Database connection strings target the internal PostgreSQL service.
- Converse endpoints point to the expected XMPP web endpoints.
- Backup root is configured before backup scripts run.
- Restore requires an explicit confirmation value.

Validation should avoid printing secret values. Error messages should name the missing variable without echoing its value.

## 10. Misconfiguration Risks

Common risks:

- Public registration is accidentally enabled.
- Open federation is accidentally enabled.
- Jitsi guests can create rooms.
- JWT secrets are left as placeholders.
- Database passwords are reused across environments.
- Production `.env` is copied into staging or development.
- Reverse proxy routes point to host ports instead of internal service names.
- Backup directories are placed inside a public web root.
- Logs contain invite tokens, JWTs, cookies, or full database URLs.
- Restore runs against the wrong environment.

Mitigations:

- Keep `.env.example` current.
- Use explicit false defaults for risky features.
- Keep startup checks strict.
- Keep backup and restore commands noisy about target paths but quiet about secrets.
- Verify production changes from a staging environment first.

## 11. Backup of Configuration

Configuration backup is needed for disaster recovery, but it must be handled carefully.

Back up:

- The active environment file or equivalent system environment export.
- Reverse proxy configuration.
- Prosody configuration.
- Jitsi configuration.
- Portal migration state.
- Backup manifests.

Do not place configuration backups in Git.

Recommended handling:

- Store configuration backup material with the same care as database backups.
- Keep production configuration backups separate from development files.
- Record which configuration version matches each backup set.
- After restore, verify registration, federation, Jitsi authentication, and admin access settings before opening the service to users.

If configuration is suspected to be exposed, restore the service with rotated secrets.

## 12. Rollback Plan

Configuration rollback should restore the last known good settings without weakening security defaults.

Rollback process:

1. Stop affected services if the current configuration is unsafe.
2. Restore the last known good environment values.
3. Confirm required variables are present.
4. Confirm registration is disabled.
5. Confirm federation is disabled or restricted.
6. Confirm Jitsi room creation remains authenticated.
7. Restart affected services.
8. Run the documented verification commands.
9. Record the rollback reason and time.

Do not roll back to a configuration that contains exposed secrets. If the previous configuration is compromised, rotate the affected secrets first and then restart the services.
