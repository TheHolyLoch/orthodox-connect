# Orthodox Connect Contributing Guidelines

## 1. Contribution Goals

Contributions should keep Orthodox Connect private, invite-only, auditable, and practical for small Orthodox communities to operate.

Goals:

- Preserve the current trust model.
- Keep public registration disabled.
- Keep open federation disabled unless a later reviewed implementation enables trusted federation.
- Keep clergy, monastic, parish admin, diocesan admin, and platform admin status administrator-controlled.
- Keep Jitsi meeting creation authenticated and role-gated.
- Keep internal service ports private unless a reviewed deployment need requires otherwise.
- Keep documentation accurate to implemented behavior.
- Keep changes small enough for file-by-file review.
- Keep real users, real secrets, real domains, private logs, and backup data out of Git.

Contributions should improve the system without adding unrelated services, changing architecture casually, or turning planned features into undocumented implementation work.

## 2. Who Can Contribute

Anyone may propose improvements, but maintainers and trusted administrators decide what is accepted.

Useful contribution areas:

- Documentation.
- Portal workflow fixes.
- Database migration review.
- Prosody and XMPP configuration review.
- Converse.js chat usability.
- Jitsi meeting access hardening.
- Reverse proxy and deployment safety.
- Backup and restore validation.
- Security review.
- Accessibility and plain-language UX.

Contributors must not need production access, real user data, real parish names, real domains, real invite links, or real secrets to work on the project. Use fake data and disposable local environments.

## 3. Code Standards Reference (AGENTS.md)

`AGENTS.md` is the source of code and documentation working standards for this repository.

Contributors should follow it for:

- File-by-file changes.
- No `sudo` commands.
- Tabs for indentation in code.
- Required file headers for files that support comments.
- Markdown style.
- `.env` and `.env.example` handling.
- Python virtual environments.
- Python import order, function style, comments, and logging.
- Shell script shebangs and executable permissions.
- Gitignore scope.
- README structure.

If a local convention conflicts with a general habit from another project, follow this repository's `AGENTS.md` and the existing Orthodox Connect docs.

## 4. File-by-File Change Rule

Changes should be easy to inspect one file at a time.

Rules:

- Keep each change scoped to the requested file or component.
- Avoid mixing application code, Docker behavior, documentation, and formatting cleanup in one change.
- Do not refactor unrelated files while fixing a focused issue.
- Do not rewrite generated or user-edited work unless the task requires it.
- Stop at manual review points when a task asks for them.
- List changed files clearly when review is requested.

Large work should be split into separate passes, such as schema, portal workflow, reverse proxy, documentation, and tests.

## 5. Branching Strategy

Use short-lived branches for reviewable work.

Suggested branch names:

```text
docs/codex-40-contributing
fix/portal-invite-expiry
feature/portal-room-access
security/prosody-registration-guard
ops/backup-restore-checks
```

Branch rules:

- Keep `main` for reviewed work.
- Base new work on the latest reviewed `main`.
- Use one branch per focused task.
- Do not combine unrelated MVP stages or design passes.
- Do not commit `.env`, backups, logs, generated service data, or production exports.
- Do not create release tags until the release checklist in `docs/CODEX-34-RELEASE-VERSIONING.md` is satisfied.

## 6. Commit Message Format

Use clear commit messages that name the area changed.

Format:

```text
area: short imperative summary
```

Examples:

```text
docs: add contributing guidelines
portal: reject revoked invite redemption
prosody: keep registration disabled
scripts: add restore confirmation check
```

Common areas:

- `docs`
- `portal`
- `prosody`
- `converse`
- `jitsi`
- `reverse-proxy`
- `scripts`
- `compose`
- `security`

For changes with operational impact, include a commit body covering the reason, tests run, migration impact, and rollback notes.

## 7. Pull Request Requirements

Pull requests should give reviewers enough context to verify the change without guessing.

Each pull request should include:

- Purpose of the change.
- Files changed.
- Linked issue or design document where relevant.
- Implementation notes for non-obvious choices.
- Commands run for validation.
- Security and privacy impact.
- Database migration impact, if any.
- Backup or restore impact, if any.
- Documentation updates, if behavior changed.
- Rollback notes for risky changes.

Pull requests must not include:

- Real secrets.
- Raw invite tokens.
- JWT signing secrets or token bodies.
- Session cookies.
- Real user data.
- Real production domains.
- Backup archives.
- Private logs.
- Copyrighted books, PDFs, cover images, or metadata dumps.

## 8. Review Process

Review should check correctness, scope, and trust-model impact before style details.

Reviewers should verify:

- The change matches the requested scope.
- Public registration remains disabled.
- Open federation remains disabled unless a reviewed trusted federation implementation explicitly changes it.
- Admin routes and actions remain role-gated.
- Users cannot self-assign privileged roles.
- Verification decisions remain tied to an admin user.
- Room access remains derived from roles, groups, explicit membership, and suspension state.
- Jitsi room creation remains authenticated and role-gated.
- Internal service ports remain private.
- Audit events remain present for privileged actions.
- Documentation does not describe planned features as implemented.

Security-sensitive changes should receive extra review from someone familiar with the relevant component.

## 9. Testing Expectations

Testing should match the risk and component changed.

Docs-only changes:

- Read the changed document for accuracy against current repository behavior.
- Confirm planned features are clearly marked as planned or future.
- Check that no real secrets, real domains, or real user data were added.
- Check markdown for repository style issues.

Application changes:

- Run the smallest relevant portal or workflow checks.
- Use fake users, fake groups, and disposable data.
- Confirm audit events for trust and access changes.
- Confirm denied paths fail closed.

Docker or deployment changes:

```bash
docker compose --env-file .env config
```

Portal database changes:

```bash
python3 -m portal.app.cli migrate
```

Backup changes:

```bash
scripts/backup.sh
scripts/list-backups.sh
```

Restore testing must use disposable data unless an operator has approved a production recovery procedure.

## 10. Documentation Requirements

Documentation must match implemented behavior.

Update documentation when a change affects:

- Setup.
- Environment variables.
- Docker services.
- Public routes.
- Database migrations.
- Portal workflows.
- Prosody or XMPP behavior.
- Converse.js behavior.
- Jitsi access.
- Backup and restore.
- Security assumptions.
- Operator procedures.

Documentation rules:

- Do not document future features as current features.
- Mark federation, Tor, IRC, bridges, library integration, mobile apps, and provisioning sync as future or design-only until implemented.
- Do not include real domains, real secrets, real users, private logs, or backup paths.
- Keep operator commands copyable in markdown code blocks.
- Keep rollback notes for risky operational changes.

## 11. Security-Sensitive Changes Process

Security-sensitive changes need tighter review and clearer rollback.

Security-sensitive areas include:

- Authentication.
- Invites.
- Verification.
- Roles and permissions.
- Room access.
- Jitsi JWT handling.
- Prosody registration.
- Prosody federation.
- Reverse proxy routes and headers.
- TLS and certificate handling.
- Backup and restore scripts.
- Logging and audit events.
- Dependency changes.
- Environment variables that contain secrets.

Process:

1. Identify the affected trust boundary.
2. Confirm the relevant CODEX design document supports the change.
3. Keep the change minimal.
4. Fail closed on missing or invalid configuration.
5. Avoid logging secrets or token bodies.
6. Add or update validation steps.
7. Document rollback steps.
8. Rotate any exposed secrets before returning service to users.

Architecture changes should be documented in the relevant CODEX design document before implementation.

## 12. Dependency Policy

Dependencies should be added only when they solve a real problem.

Rules:

- Prefer the standard library and existing project dependencies where practical.
- Prefer mature F/OSS services already selected by the project for core protocol work.
- Do not add a dependency for docs-only work.
- Do not add external SaaS providers as a dependency.
- Review licenses before adding a dependency.
- Review security, maintenance status, and operational impact.
- Keep Docker image changes explicit and documented.
- Keep dependency changes separate from unrelated feature work.

If a dependency affects authentication, authorization, logging, backups, cryptography, file handling, or public routing, treat it as security-sensitive.

## 13. Issue Tracking Model

Issues should describe work without leaking private data.

Useful issue categories:

- `bug`
- `docs`
- `security`
- `operations`
- `enhancement`
- `design`
- `question`

Issue reports should include:

- Component affected.
- Current behavior.
- Expected behavior.
- Steps to reproduce with fake data.
- Environment type, such as local, staging, or production.
- Relevant command output with secrets removed.
- Security or privacy impact.
- Suggested rollback or containment, if known.

Issues must not include:

- Real passwords.
- Raw invite links.
- Recovery tokens.
- JWT secrets or token bodies.
- Session cookies.
- Real user records.
- Private verification notes.
- Private room content.
- Full production logs.
- Backup archives.

Security issues with active abuse or exposed secrets should be handled through a private maintainer or operator path before public detail is posted.

## 14. Rollback Plan

Every risky contribution should have a rollback path.

Rollback process:

1. Identify the affected component and commit.
2. Stop or disable the affected public route or workflow if exposure is possible.
3. Preserve audit events, logs, backups, and operator notes needed for review.
4. Revert the faulty change or restore the last known-good configuration.
5. Run the relevant validation checks.
6. Confirm public registration remains disabled.
7. Confirm open federation remains disabled.
8. Confirm Jitsi authentication remains enabled.
9. Confirm admin routes remain role-gated.
10. Confirm internal service ports remain private.
11. Rotate exposed or suspected secrets.
12. Record the rollback result.

Rollback must not delete portal users, groups, roles, invites, verification records, rooms, meetings, audit events, Prosody data, Jitsi state, backups, or unrelated service configuration.
