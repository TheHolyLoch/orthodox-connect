# Orthodox Connect MVP Passes

## Current MVP Status

Stages 1 through 14 have been implemented or documented in the repository.

Current implementation status:

| Stage | Area                       | Status       |
| ----- | -------------------------- | ------------ |
| 1     | Repository skeleton        | Complete     |
| 2     | Docker Compose skeleton    | Complete     |
| 3     | Reverse proxy              | Complete     |
| 4     | Prosody                    | Complete     |
| 5     | Web chat frontend          | Complete     |
| 6     | Portal database model      | Complete     |
| 7     | Invite workflow            | Complete     |
| 8     | Manual verification        | Complete     |
| 9     | Room access model          | Complete     |
| 10    | Jitsi integration          | Complete     |
| 11    | Basic admin UI             | Complete     |
| 12    | Local backups              | Complete     |
| 13    | Hardening pass             | Complete     |
| 14    | Documentation pass         | Current pass |

Known MVP limits:

- Portal production packaging is not done.
- Prosody account provisioning from portal data is not done.
- Email delivery is not implemented.
- Library and Tor services are later scope.

## Pass Rules

- Work one pass at a time.
- Change only the files listed in the pass.
- Stop at the manual review point before starting the next pass.
- Do not add implementation outside the pass scope.
- Do not commit `.env`, secrets, logs, backups, generated data, or production state.

## 1. Repository Skeleton

**Goal:** Create the project structure, license, baseline ignore rules, and top-level docs placeholders.

**Files allowed to change:**

- `.gitignore`
- `LICENSE`
- `README.md`
- `docs/CODEX-00-PROJECT-BRIEF.md`
- `docs/CODEX-01-ARCHITECTURE.md`
- `docs/CODEX-02-DEPLOYMENT-DOCKER.md`
- `docs/CODEX-03-IDENTITY-VERIFICATION.md`
- `docs/CODEX-04-SECURITY-MODEL.md`
- `docs/CODEX-05-MVP-PASSES.md`

**Exact expected output:**

- Required docs exist.
- `LICENSE` contains the ISC license.
- `.gitignore` excludes `.env`, logs, backups, local databases, caches, and generated state.
- `README.md` identifies Orthodox Connect as a planning-stage F/OSS communications platform.
- No application code exists yet.

**Manual review point:** Confirm the skeleton matches the intended project shape before adding deployment files.

**Test command or verification step:**

```bash
find . -maxdepth 3 -type f | sort
git status --short
```

## 2. Docker Compose Skeleton

**Goal:** Add non-secret Docker Compose structure with placeholder services and environment templates.

**Files allowed to change:**

- `docker-compose.yml`
- `.env.example`
- `.gitignore`
- `README.md`
- `docs/CODEX-02-DEPLOYMENT-DOCKER.md`

**Exact expected output:**

- Compose file defines service names for reverse proxy, portal, postgres, Prosody, Converse.js frontend, and Jitsi components.
- Compose file defines planned networks and volumes.
- `.env.example` lists required variables with placeholder values only.
- `.env` remains uncommitted.
- No Dockerfiles or application source are introduced in this pass.

**Manual review point:** Confirm service names, networks, volumes, and environment variable names before service-specific configuration begins.

**Test command or verification step:**

```bash
docker compose config
git status --short
```

## 3. Reverse Proxy

**Goal:** Add reverse proxy configuration for local and production routing.

**Files allowed to change:**

- `docker-compose.yml`
- `.env.example`
- `reverse-proxy/`
- `docs/CODEX-02-DEPLOYMENT-DOCKER.md`

**Exact expected output:**

- Reverse proxy service routes portal, chat frontend, Prosody browser transport, and Jitsi web traffic.
- WebSocket upgrade routing is configured for XMPP and Jitsi paths.
- HTTP to HTTPS behavior is documented or configured for production.
- Internal service ports are not published unless required.

**Manual review point:** Confirm routing names and public domains before configuring backend services.

**Test command or verification step:**

```bash
docker compose config
docker compose up reverse-proxy
```

## 4. Prosody

**Goal:** Add Prosody configuration for invite-controlled XMPP accounts and multi-user chat.

**Files allowed to change:**

- `docker-compose.yml`
- `.env.example`
- `prosody/`
- `docs/CODEX-01-ARCHITECTURE.md`
- `docs/CODEX-04-SECURITY-MODEL.md`

**Exact expected output:**

- Prosody service starts from Compose.
- Public registration is disabled.
- Local XMPP domain and MUC domain are defined.
- Browser transport endpoint is available behind the reverse proxy.
- Federation is disabled by default.
- Admin account setup is documented through environment or setup steps without committing secrets.

**Manual review point:** Confirm XMPP domain, MUC domain, registration policy, and federation default.

**Test command or verification step:**

```bash
docker compose config
docker compose up prosody
docker compose logs prosody
```

## 5. Web Chat Frontend

**Goal:** Add a beginner-friendly web XMPP client entrypoint using Converse.js or the selected alternative.

**Files allowed to change:**

- `docker-compose.yml`
- `.env.example`
- `frontend/`
- `reverse-proxy/`
- `docs/CODEX-01-ARCHITECTURE.md`

**Exact expected output:**

- Chat frontend loads in a browser.
- Frontend points to the configured Prosody browser transport.
- No hardcoded production secrets exist in frontend files.
- Login reaches Prosody but account provisioning remains controlled by the portal plan.

**Manual review point:** Confirm the selected web client is acceptable before portal work starts.

**Test command or verification step:**

```bash
docker compose config
docker compose up converse prosody reverse-proxy
```

## 6. Portal Database Model

**Goal:** Add the conceptual database model as actual migration or model files for portal state.

**Files allowed to change:**

- `portal/`
- `docker-compose.yml`
- `.env.example`
- `docs/CODEX-03-IDENTITY-VERIFICATION.md`

**Exact expected output:**

- Portal has database models or migrations for users, invitations, parishes, groups, memberships, roles, verification records, rooms, room access policies, suspension, recovery requests, and audit events.
- PostgreSQL connection uses environment variables.
- No seed data contains real people, real parishes, or secrets.
- Model names match the identity verification plan unless reviewed first.

**Manual review point:** Confirm schema shape before adding workflows that depend on it.

**Test command or verification step:**

```bash
docker compose config
docker compose up postgres
```

## 7. Invite Workflow

**Goal:** Implement invite-only registration and invitation state handling.

**Files allowed to change:**

- `portal/`
- `docs/CODEX-03-IDENTITY-VERIFICATION.md`
- `README.md`

**Exact expected output:**

- Admin can create, revoke, and view invitations.
- Invite acceptance creates a limited pending account.
- Invite tokens expire and are single-use unless explicitly configured otherwise.
- Accepted accounts cannot self-assign verified or privileged roles.
- Invitation actions create audit records.

**Manual review point:** Test invite creation and acceptance manually before manual approval is added.

**Test command or verification step:**

```bash
docker compose up portal postgres
```

## 8. Manual Verification Workflow

**Goal:** Add approval, denial, clergy verification, monastic verification, and audit trail workflows.

**Files allowed to change:**

- `portal/`
- `docs/CODEX-03-IDENTITY-VERIFICATION.md`
- `docs/CODEX-04-SECURITY-MODEL.md`

**Exact expected output:**

- Admin can approve or deny pending users.
- Admin can grant and revoke `clergy_verified` and `monastic_verified`.
- Users cannot self-assert clergy or monastic labels.
- Verification decisions create audit records.
- Suspended users do not appear as active verified users.

**Manual review point:** Confirm verification labels, audit records, and revoked status behavior.

**Test command or verification step:**

```bash
docker compose up portal postgres
```

## 9. Role-Based Room Access Model

**Goal:** Connect roles, memberships, and room policies to Prosody room access.

**Files allowed to change:**

- `portal/`
- `prosody/`
- `docs/CODEX-01-ARCHITECTURE.md`
- `docs/CODEX-03-IDENTITY-VERIFICATION.md`
- `docs/CODEX-04-SECURITY-MODEL.md`

**Exact expected output:**

- Portal can define rooms and access policies.
- Room access can be based on role, parish membership, group membership, explicit membership, or verification status.
- Prosody room state reflects approved policy changes.
- Suspended users lose room access.
- Shared inter-group channels require explicit membership.

**Manual review point:** Confirm access behavior for guest, inquirer, member, clergy, monastic, parish admin, and suspended accounts.

**Test command or verification step:**

```bash
docker compose up portal postgres prosody converse reverse-proxy
```

## 10. Jitsi Integration

**Goal:** Add authenticated Jitsi meeting access tied to approved users and room policy.

**Files allowed to change:**

- `docker-compose.yml`
- `.env.example`
- `jitsi/`
- `portal/`
- `reverse-proxy/`
- `docs/CODEX-01-ARCHITECTURE.md`
- `docs/CODEX-04-SECURITY-MODEL.md`

**Exact expected output:**

- Jitsi services start through Compose.
- Meeting access requires authentication or validated room access.
- Anonymous public room creation is disabled.
- Room creation can be limited to approved roles.
- Meeting links do not grant access by themselves.

**Manual review point:** Confirm meeting creation, join permissions, and denied access behavior.

**Test command or verification step:**

```bash
docker compose config
docker compose up jitsi-web jitsi-prosody jitsi-jicofo jitsi-jvb
```

## 11. Basic Admin UI

**Goal:** Build the minimum admin interface for the MVP workflows.

**Files allowed to change:**

- `portal/`
- `README.md`
- `docs/CODEX-03-IDENTITY-VERIFICATION.md`

**Exact expected output:**

- Admin can view pending users, active users, suspended users, invitations, roles, verification records, rooms, and audit events.
- Admin can create invites, approve users, assign roles, verify clergy, verify monastics, suspend users, restore users, and manage room access.
- UI avoids exposing internal verification notes to non-admin users.
- Forms protect against accidental privileged role assignment.

**Manual review point:** Walk through every admin action in a local test instance.

**Test command or verification step:**

```bash
docker compose up portal postgres prosody converse reverse-proxy
```

## 12. Backups

**Goal:** Add backup and restore tooling for MVP state.

**Files allowed to change:**

- `scripts/`
- `docker-compose.yml`
- `.env.example`
- `.gitignore`
- `README.md`
- `docs/CODEX-02-DEPLOYMENT-DOCKER.md`
- `docs/CODEX-04-SECURITY-MODEL.md`

**Exact expected output:**

- Backup script covers PostgreSQL logical dumps, Prosody data, Prosody configuration, portal uploaded files if present, Jitsi configuration, and reverse proxy certificate data if managed by the stack.
- Restore procedure is documented.
- Backup output path is excluded from Git.
- Scripts that are shell files are executable.
- No real backup data is committed.

**Manual review point:** Run a local backup and restore against disposable data before production hardening.

**Test command or verification step:**

```bash
find scripts -type f -name '*.sh' -exec test -x {} \;
git status --short
```

## 13. Hardening Pass

**Goal:** Reduce public attack surface and check security defaults across services.

**Files allowed to change:**

- `docker-compose.yml`
- `.env.example`
- `.gitignore`
- `portal/`
- `prosody/`
- `jitsi/`
- `reverse-proxy/`
- `docs/CODEX-04-SECURITY-MODEL.md`

**Exact expected output:**

- Public registration remains disabled.
- Federation remains disabled by default.
- Internal ports are not published unless required.
- Debug logging is off by default in production settings.
- Secrets are only referenced through environment variables or secret files.
- Admin and verification actions are audited.
- Suspended accounts cannot access portal, chat, rooms, or meetings.

**Manual review point:** Review all public ports, secret handling, logs, room access, and admin workflows before documentation polish.

**Test command or verification step:**

```bash
docker compose config
git status --short
```

## 14. Documentation Pass

**Goal:** Update operator and user-facing documentation after MVP behavior is verified.

**Files allowed to change:**

- `README.md`
- `docs/`
- `.env.example`

**Exact expected output:**

- README explains purpose, requirements, setup, usage, backups, and security limits.
- Docs match the implemented MVP behavior.
- `.env.example` matches all required settings.
- Open questions are clearly marked.
- No docs claim end-to-end security beyond verified component behavior.

**Manual review point:** Read docs as a new operator and confirm setup can be followed without hidden steps.

**Test command or verification step:**

```bash
rg 'TODO|TBD|CHANGE_ME|secret|password' README.md docs .env.example
git status --short
```
