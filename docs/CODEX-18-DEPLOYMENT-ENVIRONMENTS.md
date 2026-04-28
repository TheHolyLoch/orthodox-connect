# Orthodox Connect Deployment Environments

## Environment Goals

Deployment environments should let operators test changes before production without mixing real community data, secrets, domains, or backups.

Goals:

- Keep production stable and recoverable.
- Keep local development fast and disposable.
- Keep staging close enough to production to catch deployment issues.
- Keep secrets separate per environment.
- Keep data separate per environment.
- Keep public registration disabled in every environment.
- Keep federation disabled unless a later reviewed policy enables it.
- Keep Jitsi room creation authenticated in every environment.
- Test backup and restore before production changes.
- Promote changes only after the relevant checks pass.

Environment separation is a safety control. It must not depend on user memory alone.

## Environment Types

### Local Development

Local development is for building, reviewing, and testing with disposable data.

Expected traits:

- Runs on a developer workstation or disposable local VM.
- Uses `.localhost`, loopback, or test-only hostnames.
- Uses fake users, fake groups, fake rooms, and fake meeting names.
- Uses local `.env` values with no production secrets.
- May use self-signed or local-only TLS when needed for browser behavior.
- May reset volumes often.
- May run only the services needed for the current task.
- Must not contain real parish, diocesan, monastic, invite, verification, meeting, or chat data.

Local development should catch syntax errors, migration errors, basic portal workflow bugs, and Compose configuration problems.

### Staging

Staging is for testing production-like deployment behavior before production.

Expected traits:

- Runs on infrastructure separate from production.
- Uses staging-only domains or local operator-only hostnames.
- Uses staging-only `.env` values and secrets.
- Uses production-like Docker Compose service layout.
- Uses disposable or scrubbed test data only.
- Exercises Caddy routing, Prosody browser transports, Converse.js, portal workflows, Jitsi JWT access, and backup scripts.
- May test certificate issuance only with staging or test domains controlled by the operator.
- Must not contain production `.env`, production database dumps, production Prosody data, production Jitsi config, or production Caddy data.

Staging should be the last review point before production.

### Production

Production is the live Orthodox Connect instance for a parish, diocese, monastery, or trusted community.

Expected traits:

- Uses real operator-controlled domains.
- Uses valid TLS certificates.
- Uses production-only secrets.
- Uses persistent data volumes.
- Uses regular backups.
- Uses access limited to trusted operators and approved administrators.
- Keeps public registration disabled.
- Keeps open federation disabled.
- Keeps internal service ports private unless a reviewed deployment requires otherwise.
- Runs only reviewed configuration.

Production changes should be deliberate, backed up, and tested in staging first where practical.

## Differences Between Environments

| Area              | Local Development                    | Staging                         | Production |
| ----------------- | ------------------------------------ | ------------------------------- | ---------- |
| Data              | Disposable fake data.                | Disposable or scrubbed data.    | Real community data. |
| Secrets           | Local fake secrets.                  | Staging-only secrets.           | Production-only secrets. |
| Domains           | `.localhost` or local-only names.    | Staging-only names.             | Real operator-controlled names. |
| TLS               | Local-only or self-signed if needed. | Staging/test certificates.      | Valid public certificates. |
| Backups           | Optional disposable checks.          | Required restore testing.       | Required regular backups. |
| Monitoring        | Manual logs and checks.              | Production-like checks.         | Operator-reviewed checks and alerts. |
| Access            | Developers only.                     | Operators and testers only.     | Approved users and administrators. |
| Data retention    | Short or reset often.                | Short and disposable.           | Policy-defined. |
| Federation        | Disabled.                            | Disabled unless testing design. | Disabled unless approved later. |
| Public signup     | Disabled.                            | Disabled.                       | Disabled. |

The same commit may move across environments, but the data and secrets must not.

## Environment-Specific Configuration

Configuration should come from environment variables and local operator-owned `.env` files.

Rules:

- Do not commit `.env`.
- Do not commit real secrets.
- Do not reuse production `.env` in local development or staging.
- Do not reuse staging secrets in production.
- Keep environment names explicit in operator notes and prompts.
- Keep `XMPP_REGISTRATION_ENABLED=false` in every environment.
- Keep `JITSI_ENABLE_AUTH=1` in every environment.
- Keep `JITSI_ENABLE_GUESTS=0` for MVP policy unless a later reviewed change allows guests in a controlled way.
- Keep `PORTAL_DATABASE_URL` pointed at the correct environment database.
- Keep backup paths separate by environment.

Suggested environment labels:

| Variable Pattern | Purpose |
| ---------------- | ------- |
| `APP_ENV=local`  | Local development marker if implemented later. |
| `APP_ENV=staging` | Staging marker if implemented later. |
| `APP_ENV=production` | Production marker if implemented later. |

These labels are design notes only. They do not require changes to `.env.example` or application code in this pass.

## Secrets Handling Model

Secrets must be unique per environment.

Secret rules:

- Generate production secrets outside Git.
- Store production secrets in operator-controlled storage.
- Give staging its own secrets.
- Give local development fake or disposable secrets.
- Rotate secrets after suspected exposure.
- Never copy production `.env` into staging or local development.
- Never use real invite links, recovery tokens, JWT secrets, database passwords, TLS private keys, onion keys, or backup encryption keys in docs or tests.
- Treat Caddy ACME data, Jitsi generated config, Prosody data, PostgreSQL dumps, and backup archives as sensitive.

Production secrets should be available to at least two trusted operators through a reviewed emergency process, not through the repository.

## Domain and Hostname Strategy

Hostnames should be environment-specific and controlled.

Local development:

- Prefer `.localhost` names, loopback names, or entries in local hosts files.
- Use fake domains only.
- Do not request public certificates for casual local work.

Staging:

- Use staging-only hostnames controlled by the operator.
- Do not use production hostnames.
- Do not publish staging links to ordinary users.
- Do not use staging as a backup production endpoint unless a disaster plan explicitly says so.

Production:

- Use real operator-controlled hostnames.
- Use valid TLS certificates.
- Keep public routes limited to reviewed services.
- Keep internal service hostnames and ports private.

Hostname categories should remain consistent:

| Category | Purpose |
| -------- | ------- |
| Portal   | Admin and portal workflows. |
| Chat     | Converse.js web chat frontend. |
| XMPP     | Browser XMPP transports routed through Caddy. |
| Meet     | Jitsi Meet web access. |
| Library  | Reserved for later library access. |

Do not add real domains in repository documentation.

## Data Separation Policy

Data must not move from production into lower environments unless it has been reviewed and scrubbed.

Rules:

- Local development uses fake data.
- Staging uses fake or scrubbed data.
- Production uses real community data.
- Production database dumps must not be loaded into local development.
- Production Prosody data must not be loaded into local development.
- Production Jitsi config and generated secrets must not be loaded into local development.
- Production Caddy certificate data must not be loaded into local development.
- Production backups must not be copied to casual test environments.
- Test accounts, rooms, invites, and meetings must be clearly fake.

If a production issue requires debugging with production data, operators should use a controlled production maintenance workflow or a locked-down private restore target approved for sensitive data.

## Deployment Promotion Flow

Promotion should move code and reviewed configuration forward, not data or secrets.

Recommended flow:

1. Develop and review locally with fake data.
2. Run local syntax, migration, and workflow checks.
3. Apply the change to staging with staging secrets and staging data.
4. Run staging validation for affected services.
5. Create or confirm a recent production backup.
6. Record the commit, environment, backup timestamp, and operator performing the deployment.
7. Apply the reviewed change to production.
8. Run post-deployment validation.
9. Monitor logs and audit events for unexpected behavior.

Promotion gates:

- Compose config renders cleanly.
- Portal migrations run cleanly where relevant.
- Public registration remains disabled.
- Federation remains disabled.
- Jitsi authentication remains enabled.
- Internal service ports remain private.
- Backup and restore expectations are satisfied for the environment.

No CI/CD tooling is defined in this document. This is a manual promotion model until tooling is explicitly designed.

## Rollback Between Environments

Rollback should happen inside the affected environment.

Rules:

- Do not roll production data back by copying staging data into production.
- Do not roll staging back by copying production secrets into staging.
- Do not repair local development by importing production data.
- Use backups from the same environment.
- Preserve audit records and logs needed for review.
- Rotate any environment secret exposed during the rollback event.

Rollback order:

1. Stop affected public routes or services if needed.
2. Identify the last known-good commit or configuration for that environment.
3. Restore the previous configuration or service state.
4. Restore data from an environment-matched backup only if needed.
5. Run validation checks for that environment.
6. Record the rollback result.

Production rollback should favor preserving trust records and audit history over speed when there is no active safety issue.

## Testing Requirements Per Environment

### Local Development

Required local checks:

- `docker compose config` with local `.env` where relevant.
- Portal migrations against local disposable PostgreSQL.
- Invite creation, revocation, and redemption with fake users when affected.
- Verification request approval and rejection with fake users when affected.
- Room access checks with fake users when affected.
- Jitsi token issuance with fake meetings when affected.
- Backup scripts only against disposable data.

Local tests should not use production domains, real users, or real secrets.

### Staging

Required staging checks:

- Compose config renders with staging `.env`.
- Public staging routes load through Caddy.
- Prosody browser transport paths work through staging routes.
- Converse.js points at staging XMPP transport URLs.
- Portal admin UI starts and remains role-gated.
- Invite, verification, room, meeting, and audit workflows work with fake data.
- Jitsi requires JWT authentication.
- Backup script completes.
- Restore is tested against staging or disposable data before production changes that affect persistence.

Staging should catch routing, certificate, service startup, and environment-variable problems before production.

### Production

Required production checks:

- Confirm a recent backup exists before risky changes.
- Confirm deployment uses production `.env`.
- Confirm public HTTPS routes load.
- Confirm Caddy certificates are valid.
- Confirm public registration remains disabled.
- Confirm federation remains disabled.
- Confirm Jitsi authentication remains enabled.
- Confirm portal admin access works for approved admins.
- Confirm audit events are being written for privileged actions.
- Confirm backup scripts still run after deployment.

Production validation should use disposable test accounts only where the deployment policy allows it.

## Access Control Per Environment

Access should be narrower as data sensitivity increases.

Local development:

- Developers may have full local admin control.
- Data must be fake.
- Local admin accounts must not resemble real production accounts.

Staging:

- Access limited to trusted operators, developers, and named testers.
- Staging admin accounts must be separate from production accounts.
- Staging should not be open to ordinary users.
- Staging links should not be posted publicly.

Production:

- Access limited to approved users.
- Admin access limited to trusted administrators.
- Platform admin access limited to trusted operators.
- Operators must not share accounts.
- Emergency access records should stay outside Git.

Privileged production access should be reviewed regularly.

## Backup Differences Per Environment

Backup policy should match data value and sensitivity.

Local development:

- Backups are optional.
- Backups should contain fake data only.
- Local backups may be deleted frequently.

Staging:

- Backups are required before testing restore, migrations, or persistence changes.
- Staging backups must not include production data.
- Retention should be short unless staging is used for formal release validation.

Production:

- Backups are required.
- Backups should include PostgreSQL, Prosody data/config, Jitsi config/data, reverse proxy data where managed by the stack, and backup manifests.
- Backups must be protected like sensitive community records.
- Restore should be tested on a schedule with disposable or approved data.
- Production backup access should be limited to trusted operators.

Backups from one environment should not be restored into another environment unless the data has been reviewed and the target is approved for that sensitivity.

## Monitoring Differences Per Environment

Monitoring should match the environment's purpose.

Local development:

- Use terminal output, Docker logs, and manual checks.
- Debug logging may be used briefly with fake data.
- No external monitoring provider is needed.

Staging:

- Use production-like health checks where practical.
- Watch startup, routing, migration, and backup behavior.
- Keep logs short-lived.
- Do not alert ordinary users from staging.

Production:

- Monitor service availability, TLS renewal, database connectivity, Prosody transport, Jitsi availability, backup success, disk usage, and repeated authentication failures.
- Keep debug logging off by default.
- Keep log retention short unless policy requires otherwise.
- Treat logs as sensitive.
- Review logs and audit events after deployments.

Monitoring must not collect message bodies, invite tokens, recovery tokens, JWT bodies, session cookies, `.env` contents, or private notes.

## Rollback Plan

Environment design rollback should restore the previous environment policy without changing application behavior.

Rollback steps:

1. Stop using the faulty environment guidance.
2. Reapply the previous environment naming, access, or promotion policy.
3. Confirm no production secrets were copied into local development or staging.
4. Confirm no production data was copied into local development or staging.
5. Confirm production routes still use production hostnames.
6. Confirm staging routes do not use production hostnames.
7. Confirm backups remain separated by environment.
8. Rotate any secret that crossed environment boundaries.
9. Preserve audit records and incident notes.
10. Record what was reverted and why.

Rollback must not delete production users, roles, groups, invites, verification records, rooms, meetings, audit events, backups, Prosody data, Jitsi state, or unrelated service configuration.
