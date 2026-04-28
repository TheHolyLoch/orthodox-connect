# Orthodox Connect Release and Versioning

## 1. Versioning Goals

Release and versioning policy should make Orthodox Connect upgrades predictable for small self-hosted deployments.

Goals:

- Give operators a clear way to identify what version is running.
- Separate code, configuration, database, and backup concerns during upgrades.
- Make database migrations visible before production deployment.
- Keep rollback possible before risky changes.
- Keep documentation aligned with implemented behavior.
- Keep public registration disabled through every release.
- Keep open federation disabled unless a later reviewed release explicitly changes that policy.
- Keep Jitsi room creation authenticated and role-gated.
- Avoid real secrets, real domains, real users, and real tags in repository documentation.

Release process is manual until a later document designs CI/CD.

## 2. Version Format

Orthodox Connect should use a Semantic Versioning style format:

```text
MAJOR.MINOR.PATCH
```

Git tags may use a leading `v`:

```text
vMAJOR.MINOR.PATCH
```

Pre-release versions may append a pre-release label:

```text
v0.1.0-alpha.1
v0.1.0-beta.1
v0.1.0-rc.1
```

Build metadata should not be used for deployment decisions. Operators should deploy by reviewed commit or release tag, not by untracked local changes.

## 3. Patch, Minor, and Major Changes

### Patch

A patch release fixes or clarifies existing behavior without changing compatibility.

Patch changes may include:

- Bug fixes.
- Security hardening that does not require operator migration.
- Documentation corrections.
- Small script fixes.
- Test or validation updates.
- Dependency updates that do not change behavior or configuration.

Patch releases should not:

- Add required environment variables without safe defaults.
- Change database schema in a way that requires manual data repair.
- Change public routes.
- Change room, role, verification, invite, or meeting access semantics.
- Expose new ports or services.

### Minor

A minor release adds backward-compatible functionality.

Minor changes may include:

- New implemented portal workflows.
- New optional environment variables.
- Additive database migrations.
- New admin views.
- New backup or restore checks.
- New internal validation commands.
- New documentation for implemented behavior.

Minor releases must keep existing supported configuration working unless the changelog clearly marks a deprecation.

### Major

A major release includes breaking changes or operational changes that require stronger review.

Major changes include:

- Required environment variable renames or removals.
- Incompatible database migrations.
- Destructive schema changes.
- Service layout changes that affect backups, restore, routing, or data ownership.
- Changes to the portal trust model.
- Changes that broaden registration, federation, meeting creation, or room access behavior.
- Removal of an implemented workflow.
- Changes requiring production downtime or manual data migration.

Major releases require a tested rollback path and a fresh production backup before deployment.

## 4. MVP Version Definition

The MVP release line should remain pre-1.0 until production packaging, account provisioning, login hardening, and operator validation are mature enough for normal production adoption.

Recommended MVP version target:

```text
0.1.0
```

The MVP version means the repository contains the first coherent self-hosted stack for:

- Reverse proxy routing.
- PostgreSQL-backed portal data.
- Invite workflow.
- Manual verification workflow.
- Role-based room access model.
- Authenticated Jitsi meeting access.
- Minimal admin UI.
- Prosody and Converse.js chat foundation.
- Local backup and restore scripts.
- Current documentation and design notes.

The MVP version does not mean every planned feature is implemented. Trusted federation, Tor access, library integration, IRC fallback, full provisioning sync, mobile app work, external APIs, and advanced moderation remain later scope unless a later release implements them.

## 5. Pre-release Tags

Pre-release tags communicate deployment risk.

| Tag Type | Meaning |
| -------- | ------- |
| `alpha`  | Incomplete or early review build. Use disposable data only. |
| `beta`   | Feature complete for the target release, but still under staging review. |
| `rc`     | Release candidate with no known release blockers. Restore testing should be complete. |

Pre-release examples:

```text
v0.1.0-alpha.1
v0.1.0-beta.1
v0.1.0-rc.1
```

Pre-release builds should not be used for production parish, diocesan, monastic, or community data unless the operator accepts the risk and has a tested backup.

## 6. Changelog Requirements

Every release should have changelog notes before tagging.

Changelog entries should include:

- Version number.
- Release date.
- Changed components.
- Security changes.
- Database migrations.
- Required environment variable changes.
- Backup and restore notes.
- Operator action required before upgrade.
- Known limitations.
- Rollback notes.

Changed components should be listed by area where relevant:

- `portal`
- `prosody`
- `converse`
- `jitsi`
- `reverse-proxy`
- `scripts`
- `docker-compose.yml`
- `.env.example`
- `docs`

Changelog entries must not include real secrets, raw tokens, real user data, production domains, private backup paths, or private incident details.

## 7. Release Checklist

Before creating a release tag, complete the relevant checks.

Checklist:

1. Confirm the worktree is clean.
2. Confirm documentation matches implemented behavior.
3. Confirm `.env.example` lists required variables without real secrets.
4. Run `docker compose config` with reviewed environment values.
5. Run portal migrations against disposable or staging data when migrations changed.
6. Check invite, verification, room, meeting, and audit workflows when affected.
7. Confirm public registration remains disabled.
8. Confirm open federation remains disabled.
9. Confirm Jitsi authentication remains enabled.
10. Confirm admin routes require approved admin roles.
11. Confirm internal service ports remain private except reviewed media ports.
12. Run backup scripts where persistence changed.
13. Run a restore test before production use for releases that affect data or backups.
14. Review logs and scripts for secret leakage.
15. Write changelog notes.
16. Record rollback requirements.

No CI/CD requirement is added by this checklist.

## 8. Database Migration Handling

Database migrations are release-sensitive because PostgreSQL stores portal trust state.

Migration rules:

- Use ordered SQL migration files in `portal/migrations/`.
- Prefer additive migrations.
- Keep migrations small and reviewable.
- Do not include real users, real groups, real rooms, real invites, real meetings, or real secrets.
- Back up PostgreSQL before production migrations.
- Test migrations against disposable data before production.
- Test migrations in staging before risky production changes where practical.
- Preserve audit history.
- Keep public registration disabled during and after migration.
- Keep open federation disabled during and after migration.

Future migrations should include:

- Purpose.
- Expected data impact.
- Manual validation command or check.
- Rollback note.
- Downtime expectation, if any.

Destructive migrations require a major release unless the affected data is clearly unused test data and the operator has approved the cleanup.

## 9. Backward Compatibility Policy

Pre-1.0 releases use best-effort compatibility. Breaking changes may still happen, but they must be documented clearly before deployment.

After 1.0:

- Patch releases must be backward-compatible.
- Minor releases should be backward-compatible.
- Major releases may include breaking changes.

Compatibility expectations:

- Existing environment variable names should remain valid where practical.
- Existing database records should remain readable after normal migrations.
- Existing audit records should remain preserved.
- Existing backup and restore workflows should remain documented.
- Existing public routes should not change without release notes.
- Access-control behavior should not silently widen.

Future external APIs should use explicit versioning and separate deprecation notes before breaking clients.

## 10. Rollback Between Versions

Rollback must treat code, configuration, database state, and service data separately.

Rollback rules:

- Use same-environment backups only.
- Preserve current data for review before restoring older data.
- Stop affected public routes or writes if current behavior is unsafe.
- If no database migration ran, rollback may be a code and configuration change.
- If a database migration ran, rollback may require restoring a backup.
- Do not delete audit events to hide a bad release.
- Rotate secrets if logs, tokens, `.env` values, or backups were exposed.
- Validate public registration, federation, Jitsi auth, admin roles, and internal ports after rollback.

Production rollback should use a backup taken before the release unless a reviewed migration rollback path exists.

## 11. Deployment Sequencing

Deployment should move from lower-risk environments to production.

Recommended sequence:

1. Review changes locally with fake data.
2. Run local configuration and migration checks.
3. Deploy to staging with staging secrets and staging data.
4. Validate affected workflows in staging.
5. Confirm a recent production backup exists.
6. Deploy reviewed code and configuration to production.
7. Run database migrations if required.
8. Start or restart services in controlled order.
9. Validate public HTTPS routes.
10. Validate portal admin access.
11. Validate chat transport routes.
12. Validate Jitsi authenticated meeting access.
13. Validate backup scripts still run.
14. Watch logs and audit events after deployment.

For releases with database changes, pause affected portal writes where practical before migration.

## 12. Documentation Update Requirements

Documentation must be updated with the release when behavior changes.

Required documentation updates:

- `README.md` for operator-facing setup, usage, backup, restore, or production notes.
- `docs/` design files when architecture, trust policy, deployment, security, or workflow assumptions change.
- `.env.example` when new variables are required or old variables are deprecated.
- Changelog notes for every release.
- Migration notes when database schema changes.
- Backup and restore notes when persistence changes.
- Security notes when exposure, authentication, authorization, or secret handling changes.

Documentation must not describe planned features as implemented. Planned federation, Tor access, library integration, IRC fallback, bridge support, external APIs, and provisioning sync should remain clearly marked as future or design-only until implemented.

## 13. Tagging Strategy (git)

Git tags should mark reviewed release commits only.

Tag format:

```text
vMAJOR.MINOR.PATCH
```

Pre-release tag format:

```text
vMAJOR.MINOR.PATCH-alpha.N
vMAJOR.MINOR.PATCH-beta.N
vMAJOR.MINOR.PATCH-rc.N
```

Tagging rules:

- Create tags only after the release checklist passes.
- Prefer annotated tags for release notes.
- Tag the exact commit operators should deploy.
- Do not tag a dirty worktree.
- Do not move a published tag except for an exceptional correction with a documented reason.
- Do not create real tags from this design document.
- Keep maintenance branches as a future option if multiple supported release lines are needed.

Tag messages should reference the changelog entry, migration notes, and rollback notes where relevant.

## 14. Rollback Plan

If this release policy is wrong or too heavy for the project, rollback should return to the previous manual release process without changing application behavior.

Rollback steps:

1. Stop using the faulty release guidance.
2. Keep existing Git history, tags, data, backups, and audit records.
3. Mark any bad release notes as withdrawn or superseded instead of deleting history.
4. Reapply the previous deployment and backup process.
5. Confirm public registration remains disabled.
6. Confirm open federation remains disabled.
7. Confirm Jitsi authentication remains enabled.
8. Confirm admin routes remain role-gated.
9. Confirm internal service ports remain private.
10. Update documentation with the corrected release policy.

Rollback of release process documentation must not delete users, groups, roles, invites, verification records, rooms, meetings, audit events, backups, Prosody data, Jitsi state, reverse proxy data, or unrelated service configuration.
