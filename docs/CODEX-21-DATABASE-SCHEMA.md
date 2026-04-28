# Orthodox Connect Portal Database Schema

## 1. Schema Goals

The portal database is the source of truth for invite-only onboarding, manual verification, roles, group membership, room access, meeting access, and audit records.

Goals:

- Store identity and access-control state in PostgreSQL.
- Keep public registration unavailable.
- Keep clergy, monastic, parish admin, diocesan admin, and platform admin status administrator-controlled.
- Keep room access derived from user state, group membership, roles, and explicit room membership.
- Keep Jitsi meeting creation and token issuance tied to portal policy.
- Preserve audit records for trust and access decisions.
- Avoid storing raw invite tokens, JWTs, passwords, session cookies, or private message content.
- Support local, staging, and production environments without real data in Git.

The schema should favor explicit state fields and audit records over hard deletion.

## 2. Table List

Current portal tables:

| Table                         | Purpose |
| ----------------------------- | ------- |
| `users`                       | Core portal account identity and account state. |
| `groups`                      | Parish, monastery, mission, ministry, shared, or administrative boundaries. |
| `group_memberships`           | User membership in groups. |
| `roles`                       | Role definitions. |
| `user_roles`                  | Role assignments to users, optionally scoped to a group. |
| `invites`                     | Invite-only onboarding records. |
| `verification_requests`       | User requests for clergy, monastic, or parish admin verification. |
| `verification_decisions`      | Admin decisions for verification requests. |
| `rooms`                       | Chat room or channel records controlled by portal policy. |
| `room_memberships`            | Explicit room membership records. |
| `meetings`                    | Jitsi meeting records created through portal policy. |
| `audit_events`                | Append-only trust and access decision events. |

Current Jitsi support tables:

| Table                         | Purpose |
| ----------------------------- | ------- |
| `meeting_guests`              | Approved guest records for a meeting. |
| `meeting_token_issuances`     | Records of issued Jitsi tokens without storing token bodies. |

## 3. Table Definitions

### `users`

| Field          | Type        | Null | Default             | Notes |
| -------------- | ----------- | ---- | ------------------- | ----- |
| `id`           | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `xmpp_jid`     | `text`      | Yes  |                     | Unique XMPP JID when provisioned. |
| `display_name` | `text`      | No   |                     | Human-readable account label. |
| `email`        | `text`      | Yes  |                     | Unique email if collected. |
| `status`       | `text`      | No   | `pending`           | One of `pending`, `approved`, `denied`, `suspended`, `disabled`. |
| `created_at`   | `timestamptz` | No | `now()`             | Creation timestamp. |
| `updated_at`   | `timestamptz` | No | `now()`             | Last update timestamp. |

Constraints:

- Primary key: `id`.
- Unique: `xmpp_jid`.
- Unique: `email`.
- Check: `status IN ('pending', 'approved', 'denied', 'suspended', 'disabled')`.

### `groups`

| Field             | Type        | Null | Default             | Notes |
| ----------------- | ----------- | ---- | ------------------- | ----- |
| `id`              | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `parent_group_id` | `uuid`      | Yes  |                     | Parent group, if nested. |
| `name`            | `text`      | No   |                     | Display name. |
| `slug`            | `text`      | No   |                     | Stable unique slug. |
| `group_type`      | `text`      | No   |                     | Group category. |
| `description`     | `text`      | Yes  |                     | Optional admin or display description. |
| `created_at`      | `timestamptz` | No | `now()`             | Creation timestamp. |
| `updated_at`      | `timestamptz` | No | `now()`             | Last update timestamp. |

Constraints:

- Primary key: `id`.
- Foreign key: `parent_group_id` references `groups(id)` with `ON DELETE SET NULL`.
- Unique: `slug`.
- Check: `group_type IN ('parish', 'monastery', 'mission', 'ministry', 'shared', 'administrative')`.

### `group_memberships`

| Field        | Type        | Null | Default             | Notes |
| ------------ | ----------- | ---- | ------------------- | ----- |
| `id`         | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `group_id`   | `uuid`      | No   |                     | Group membership target. |
| `user_id`    | `uuid`      | No   |                     | User membership target. |
| `status`     | `text`      | No   | `pending`           | Membership state. |
| `created_at` | `timestamptz` | No | `now()`             | Creation timestamp. |
| `updated_at` | `timestamptz` | No | `now()`             | Last update timestamp. |

Constraints:

- Primary key: `id`.
- Foreign key: `group_id` references `groups(id)` with `ON DELETE CASCADE`.
- Foreign key: `user_id` references `users(id)` with `ON DELETE CASCADE`.
- Unique: `(group_id, user_id)`.
- Check: `status IN ('invited', 'pending', 'active', 'suspended', 'removed')`.

Indexes:

- `idx_group_memberships_user_id` on `(user_id)`.

### `roles`

| Field         | Type        | Null | Default             | Notes |
| ------------- | ----------- | ---- | ------------------- | ----- |
| `id`          | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `name`        | `text`      | No   |                     | Stable role name. |
| `description` | `text`      | Yes  |                     | Human-readable role description. |
| `created_at`  | `timestamptz` | No | `now()`             | Creation timestamp. |

Constraints:

- Primary key: `id`.
- Unique: `name`.

Expected role names:

- `guest`
- `inquirer`
- `member`
- `parish_admin`
- `clergy_verified`
- `monastic_verified`
- `diocesan_admin`
- `platform_admin`

### `user_roles`

| Field                | Type        | Null | Default             | Notes |
| -------------------- | ----------- | ---- | ------------------- | ----- |
| `id`                 | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `user_id`            | `uuid`      | No   |                     | User receiving the role. |
| `role_id`            | `uuid`      | No   |                     | Assigned role. |
| `group_id`           | `uuid`      | Yes  |                     | Optional scope for the assignment. |
| `granted_by_user_id` | `uuid`      | Yes  |                     | Admin or system actor that granted the role. |
| `granted_at`         | `timestamptz` | No | `now()`             | Grant timestamp. |
| `revoked_at`         | `timestamptz` | Yes |                     | Soft revocation timestamp. |

Constraints:

- Primary key: `id`.
- Foreign key: `user_id` references `users(id)` with `ON DELETE CASCADE`.
- Foreign key: `role_id` references `roles(id)` with `ON DELETE CASCADE`.
- Foreign key: `group_id` references `groups(id)` with `ON DELETE CASCADE`.
- Foreign key: `granted_by_user_id` references `users(id)` with `ON DELETE SET NULL`.
- Unique: `(user_id, role_id, group_id)`.

Indexes:

- `idx_user_roles_user_id` on `(user_id)`.

Design note:

- PostgreSQL permits multiple `NULL` values in a unique constraint. A later migration may need a partial unique index for global roles where `group_id IS NULL`.

### `invites`

| Field                 | Type        | Null | Default             | Notes |
| --------------------- | ----------- | ---- | ------------------- | ----- |
| `id`                  | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `token_hash`          | `text`      | No   |                     | Hash of invite token, not raw token. |
| `created_by_user_id`  | `uuid`      | Yes  |                     | Admin that created the invite. |
| `group_id`            | `uuid`      | Yes  |                     | Optional invite group scope. |
| `expected_role_id`    | `uuid`      | Yes  |                     | Optional expected role. |
| `status`              | `text`      | No   | `unused`            | Invite state. |
| `expires_at`          | `timestamptz` | No |                     | Expiry timestamp. |
| `accepted_by_user_id` | `uuid`      | Yes  |                     | User that redeemed the invite. |
| `accepted_at`         | `timestamptz` | Yes |                     | Redemption timestamp. |
| `created_at`          | `timestamptz` | No | `now()`             | Creation timestamp. |
| `updated_at`          | `timestamptz` | No | `now()`             | Last update timestamp. |
| `reusable`            | `boolean`   | No   | `false`             | Allows more than one redemption when true. |
| `use_count`           | `integer`   | No   | `0`                 | Number of redemptions. |

Constraints:

- Primary key: `id`.
- Foreign key: `created_by_user_id` references `users(id)` with `ON DELETE SET NULL`.
- Foreign key: `group_id` references `groups(id)` with `ON DELETE SET NULL`.
- Foreign key: `expected_role_id` references `roles(id)` with `ON DELETE SET NULL`.
- Foreign key: `accepted_by_user_id` references `users(id)` with `ON DELETE SET NULL`.
- Unique: `token_hash`.
- Check: `status IN ('unused', 'accepted', 'expired', 'revoked')`.
- Check: `use_count >= 0`.

Indexes:

- `idx_invites_status` on `(status)`.
- `idx_invites_expires_at` on `(expires_at)`.
- `idx_invites_reusable` on `(reusable)`.

### `verification_requests`

| Field         | Type        | Null | Default             | Notes |
| ------------- | ----------- | ---- | ------------------- | ----- |
| `id`          | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `user_id`     | `uuid`      | No   |                     | User requesting verification. |
| `group_id`    | `uuid`      | Yes  |                     | Optional group scope. |
| `request_type` | `text`     | No   |                     | Verification type. |
| `status`      | `text`      | No   | `pending`           | Request state. |
| `note`        | `text`      | Yes  |                     | Short user or admin note. |
| `created_at`  | `timestamptz` | No | `now()`             | Creation timestamp. |
| `updated_at`  | `timestamptz` | No | `now()`             | Last update timestamp. |

Constraints:

- Primary key: `id`.
- Foreign key: `user_id` references `users(id)` with `ON DELETE CASCADE`.
- Foreign key: `group_id` references `groups(id)` with `ON DELETE SET NULL`.
- Check: `request_type IN ('clergy', 'monastic', 'parish_admin')`.
- Check: `status IN ('pending', 'approved', 'denied', 'cancelled')`.

Indexes:

- `idx_verification_requests_user_id` on `(user_id)`.
- `idx_verification_requests_status` on `(status)`.
- `idx_verification_requests_request_type` on `(request_type)`.

### `verification_decisions`

| Field                     | Type        | Null | Default             | Notes |
| ------------------------- | ----------- | ---- | ------------------- | ----- |
| `id`                      | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `verification_request_id` | `uuid`      | No   |                     | Related request. |
| `decided_by_user_id`      | `uuid`      | No   |                     | Admin making the decision. |
| `decision`                | `text`      | No   |                     | Decision value. |
| `reason`                  | `text`      | Yes  |                     | Reason, especially for denial or revocation. |
| `decided_at`              | `timestamptz` | No | `now()`             | Decision timestamp. |

Constraints:

- Primary key: `id`.
- Foreign key: `verification_request_id` references `verification_requests(id)` with `ON DELETE CASCADE`.
- Foreign key: `decided_by_user_id` references `users(id)` with `ON DELETE SET NULL`.
- Check: `decision IN ('approved', 'denied', 'revoked')`.

Indexes:

- `idx_verification_decisions_decided_by_user_id` on `(decided_by_user_id)`.

Policy:

- Every verification decision must be tied to an admin user.
- Approved decisions assign the matching role through `user_roles`.
- Decisions should create audit events.

### `rooms`

| Field               | Type        | Null | Default             | Notes |
| ------------------- | ----------- | ---- | ------------------- | ----- |
| `id`                | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `group_id`          | `uuid`      | Yes  |                     | Optional owning group. |
| `name`              | `text`      | No   |                     | Room display name. |
| `slug`              | `text`      | No   |                     | Stable unique room slug. |
| `xmpp_room_jid`     | `text`      | Yes  |                     | Prosody MUC JID when provisioned. |
| `privacy_level`     | `text`      | No   | `public_to_members` | Access scope. |
| `created_at`        | `timestamptz` | No | `now()`             | Creation timestamp. |
| `updated_at`        | `timestamptz` | No | `now()`             | Last update timestamp. |
| `created_by_user_id` | `uuid`     | Yes  |                     | Admin that created the room. |

Constraints:

- Primary key: `id`.
- Foreign key: `group_id` references `groups(id)` with `ON DELETE SET NULL`.
- Foreign key: `created_by_user_id` references `users(id)` with `ON DELETE SET NULL`.
- Unique: `slug`.
- Unique: `xmpp_room_jid`.
- Check: `privacy_level IN ('public_to_members', 'group_only', 'clergy_only', 'monastic_only', 'admin_only', 'invite_only')`.

Indexes:

- `idx_rooms_group_id` on `(group_id)`.
- `idx_rooms_privacy_level` on `(privacy_level)`.

### `room_memberships`

| Field        | Type        | Null | Default             | Notes |
| ------------ | ----------- | ---- | ------------------- | ----- |
| `id`         | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `room_id`    | `uuid`      | No   |                     | Room target. |
| `user_id`    | `uuid`      | No   |                     | User target. |
| `role`       | `text`      | No   | `member`            | Room-level role. |
| `status`     | `text`      | No   | `active`            | Room membership state. |
| `created_at` | `timestamptz` | No | `now()`             | Creation timestamp. |
| `updated_at` | `timestamptz` | No | `now()`             | Last update timestamp. |

Constraints:

- Primary key: `id`.
- Foreign key: `room_id` references `rooms(id)` with `ON DELETE CASCADE`.
- Foreign key: `user_id` references `users(id)` with `ON DELETE CASCADE`.
- Unique: `(room_id, user_id)`.
- Check: `role IN ('member', 'moderator', 'admin')`.
- Check: `status IN ('active', 'suspended', 'removed')`.

Indexes:

- `idx_room_memberships_user_id` on `(user_id)`.
- `idx_room_memberships_room_status` on `(room_id, status)`.

### `meetings`

| Field                | Type        | Null | Default             | Notes |
| -------------------- | ----------- | ---- | ------------------- | ----- |
| `id`                 | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `room_id`            | `uuid`      | Yes  |                     | Related portal room, if any. |
| `created_by_user_id` | `uuid`      | Yes  |                     | User that created the meeting. |
| `name`               | `text`      | No   |                     | Meeting display name. |
| `slug`               | `text`      | No   |                     | Stable unique meeting slug. |
| `jitsi_room_name`    | `text`      | No   |                     | Jitsi room name. |
| `allow_guests`       | `boolean`   | No   | `false`             | Whether explicit guests may join. |
| `status`             | `text`      | No   | `active`            | Meeting state. |
| `created_at`         | `timestamptz` | No | `now()`             | Creation timestamp. |
| `updated_at`         | `timestamptz` | No | `now()`             | Last update timestamp. |

Constraints:

- Primary key: `id`.
- Foreign key: `room_id` references `rooms(id)` with `ON DELETE SET NULL`.
- Foreign key: `created_by_user_id` references `users(id)` with `ON DELETE SET NULL`.
- Unique: `slug`.
- Unique: `jitsi_room_name`.
- Check: `status IN ('active', 'closed', 'cancelled')`.

Indexes:

- `idx_meetings_room_id` on `(room_id)`.
- `idx_meetings_status` on `(status)`.

Related Jitsi support:

- `meeting_guests` stores explicit guest records for meetings that allow guests.
- `meeting_token_issuances` records token issuance metadata and token IDs without storing token bodies.

### `audit_events`

| Field           | Type        | Null | Default             | Notes |
| --------------- | ----------- | ---- | ------------------- | ----- |
| `id`            | `uuid`      | No   | `gen_random_uuid()` | Primary key. |
| `actor_user_id` | `uuid`      | Yes  |                     | User or admin that caused the event. |
| `target_user_id` | `uuid`     | Yes  |                     | Affected user, if any. |
| `entity_type`   | `text`      | No   |                     | Resource type. |
| `entity_id`     | `uuid`      | Yes  |                     | Resource ID. |
| `action`        | `text`      | No   |                     | Event action. |
| `scope_group_id` | `uuid`     | Yes  |                     | Group scope, if any. |
| `metadata`      | `jsonb`     | No   | `'{}'::jsonb`       | Structured event metadata. |
| `created_at`    | `timestamptz` | No | `now()`             | Event timestamp. |

Constraints:

- Primary key: `id`.
- Foreign key: `actor_user_id` references `users(id)` with `ON DELETE SET NULL`.
- Foreign key: `target_user_id` references `users(id)` with `ON DELETE SET NULL`.
- Foreign key: `scope_group_id` references `groups(id)` with `ON DELETE SET NULL`.

Indexes:

- `idx_audit_events_actor_user_id` on `(actor_user_id)`.
- `idx_audit_events_created_at` on `(created_at)`.

Policy:

- Audit events are append-only from the application perspective.
- Corrections should create new audit events instead of editing old events.
- Audit metadata must not store passwords, invite tokens, JWT token bodies, session cookies, or private message content.

## 4. Field Names and Types

General type policy:

| Data Class             | Type          | Notes |
| ---------------------- | ------------- | ----- |
| Primary keys           | `uuid`        | Generated with `gen_random_uuid()`. |
| Foreign keys           | `uuid`        | Reference primary keys. |
| Names and slugs        | `text`        | Slugs are unique where they identify records. |
| Status fields          | `text`        | Restricted with check constraints. |
| Timestamps             | `timestamptz` | Store timezone-aware timestamps. |
| Booleans               | `boolean`     | Used for explicit true or false flags. |
| Counters               | `integer`     | Used for invite use count. |
| Structured audit data  | `jsonb`       | Used only for bounded metadata. |

Naming policy:

- Table names use plural snake_case.
- Field names use snake_case.
- Foreign keys use `{table_singular}_id` where practical.
- Actor references use `actor_user_id`, `created_by_user_id`, `granted_by_user_id`, or `decided_by_user_id` to make responsibility visible.

## 5. Primary Keys

Every table uses a UUID primary key named `id`.

Current primary keys:

- `users.id`
- `groups.id`
- `group_memberships.id`
- `roles.id`
- `user_roles.id`
- `invites.id`
- `verification_requests.id`
- `verification_decisions.id`
- `rooms.id`
- `room_memberships.id`
- `meetings.id`
- `meeting_guests.id`
- `meeting_token_issuances.id`
- `audit_events.id`

## 6. Foreign Keys

Foreign key policy:

- User-owned state normally references `users(id)`.
- Group-scoped state references `groups(id)`.
- Role assignments reference `roles(id)`.
- Room membership references `rooms(id)` and `users(id)`.
- Meeting records reference `rooms(id)` and `users(id)`.
- Audit records use `ON DELETE SET NULL` so deleted or removed records do not erase audit history.

Important relationships:

| Table                    | Field                     | References |
| ------------------------ | ------------------------- | ---------- |
| `groups`                 | `parent_group_id`         | `groups(id)` |
| `group_memberships`      | `group_id`                | `groups(id)` |
| `group_memberships`      | `user_id`                 | `users(id)` |
| `user_roles`             | `user_id`                 | `users(id)` |
| `user_roles`             | `role_id`                 | `roles(id)` |
| `user_roles`             | `group_id`                | `groups(id)` |
| `user_roles`             | `granted_by_user_id`      | `users(id)` |
| `invites`                | `created_by_user_id`      | `users(id)` |
| `invites`                | `group_id`                | `groups(id)` |
| `invites`                | `expected_role_id`        | `roles(id)` |
| `invites`                | `accepted_by_user_id`     | `users(id)` |
| `verification_requests`  | `user_id`                 | `users(id)` |
| `verification_requests`  | `group_id`                | `groups(id)` |
| `verification_decisions` | `verification_request_id` | `verification_requests(id)` |
| `verification_decisions` | `decided_by_user_id`      | `users(id)` |
| `rooms`                  | `group_id`                | `groups(id)` |
| `rooms`                  | `created_by_user_id`      | `users(id)` |
| `room_memberships`       | `room_id`                 | `rooms(id)` |
| `room_memberships`       | `user_id`                 | `users(id)` |
| `meetings`               | `room_id`                 | `rooms(id)` |
| `meetings`               | `created_by_user_id`      | `users(id)` |
| `audit_events`           | `actor_user_id`           | `users(id)` |
| `audit_events`           | `target_user_id`          | `users(id)` |
| `audit_events`           | `scope_group_id`          | `groups(id)` |

## 7. Unique Constraints

Current unique constraints:

| Table                | Constraint Fields |
| -------------------- | ----------------- |
| `users`              | `xmpp_jid` |
| `users`              | `email` |
| `groups`             | `slug` |
| `group_memberships`  | `(group_id, user_id)` |
| `roles`              | `name` |
| `user_roles`         | `(user_id, role_id, group_id)` |
| `invites`            | `token_hash` |
| `rooms`              | `slug` |
| `rooms`              | `xmpp_room_jid` |
| `room_memberships`   | `(room_id, user_id)` |
| `meetings`           | `slug` |
| `meetings`           | `jitsi_room_name` |

Design notes:

- Raw invite tokens must never be stored. Only `token_hash` is unique.
- Meeting slugs and Jitsi room names must not be treated as access grants.
- Future schema work should review partial uniqueness for active-only and global-role constraints.

## 8. Indexes

Current indexes:

| Index                                      | Table                       | Fields |
| ------------------------------------------ | --------------------------- | ------ |
| `idx_group_memberships_user_id`            | `group_memberships`         | `user_id` |
| `idx_invites_status`                       | `invites`                   | `status` |
| `idx_invites_expires_at`                   | `invites`                   | `expires_at` |
| `idx_invites_reusable`                     | `invites`                   | `reusable` |
| `idx_user_roles_user_id`                   | `user_roles`                | `user_id` |
| `idx_verification_requests_user_id`        | `verification_requests`     | `user_id` |
| `idx_verification_requests_status`         | `verification_requests`     | `status` |
| `idx_verification_requests_request_type`   | `verification_requests`     | `request_type` |
| `idx_verification_decisions_decided_by_user_id` | `verification_decisions` | `decided_by_user_id` |
| `idx_rooms_group_id`                       | `rooms`                     | `group_id` |
| `idx_rooms_privacy_level`                  | `rooms`                     | `privacy_level` |
| `idx_room_memberships_user_id`             | `room_memberships`          | `user_id` |
| `idx_room_memberships_room_status`         | `room_memberships`          | `room_id`, `status` |
| `idx_meetings_room_id`                     | `meetings`                  | `room_id` |
| `idx_meetings_status`                      | `meetings`                  | `status` |
| `idx_meeting_guests_meeting_id`            | `meeting_guests`            | `meeting_id` |
| `idx_meeting_guests_status`                | `meeting_guests`            | `status` |
| `idx_meeting_token_issuances_meeting_id`   | `meeting_token_issuances`   | `meeting_id` |
| `idx_meeting_token_issuances_user_id`      | `meeting_token_issuances`   | `user_id` |
| `idx_meeting_token_issuances_guest_id`     | `meeting_token_issuances`   | `guest_id` |
| `idx_audit_events_actor_user_id`           | `audit_events`              | `actor_user_id` |
| `idx_audit_events_created_at`              | `audit_events`              | `created_at` |

Index policy:

- Index fields used for admin lists, status filters, access checks, and audit review.
- Add indexes through migrations only after query patterns are known.
- Avoid speculative indexes that slow writes without a real query need.

## 9. Soft Delete Policy

Application workflows should prefer state changes over hard deletion.

Soft delete and disable fields:

| Table                  | Soft Delete Field |
| ---------------------- | ----------------- |
| `users`                | `status` with `disabled` or `suspended` |
| `group_memberships`    | `status` with `removed` or `suspended` |
| `user_roles`           | `revoked_at` |
| `invites`              | `status` with `revoked`, `expired`, or `accepted` |
| `verification_requests` | `status` with `denied` or `cancelled` |
| `verification_decisions` | `decision` with `revoked` |
| `room_memberships`     | `status` with `removed` or `suspended` |
| `meetings`             | `status` with `closed` or `cancelled` |
| `audit_events`         | None. Append-only. |

Hard deletion should be limited to operator cleanup, test data, or future retention workflows. Hard deletion must not be used to hide trust decisions.

## 10. Timestamp Policy

Timestamp rules:

- Use `timestamptz` for all time fields.
- Store timestamps in UTC at the application boundary.
- Use `created_at` for initial creation.
- Use `updated_at` for mutable records.
- Use action-specific timestamps where state changes need historical clarity.

Action-specific timestamps:

| Field          | Table                 | Meaning |
| -------------- | --------------------- | ------- |
| `accepted_at`  | `invites`             | Invite redemption time. |
| `granted_at`   | `user_roles`          | Role grant time. |
| `revoked_at`   | `user_roles`          | Role revocation time. |
| `decided_at`   | `verification_decisions` | Verification decision time. |
| `expires_at`   | `invites`             | Invite expiry time. |
| `expires_at`   | `meeting_guests`      | Guest access expiry time. |
| `expires_at`   | `meeting_token_issuances` | Meeting token expiry time. |

`updated_at` should be refreshed by application code or a future database trigger when mutable records change. No trigger is currently defined in the migrations.

## 11. Audit Integration

Audit events should be written for every trust or access change.

Required audited actions:

- Invite creation.
- Invite revocation.
- Invite redemption.
- Verification request creation.
- Verification approval.
- Verification rejection.
- Role assignment.
- Role revocation.
- Group membership changes.
- Room creation.
- Room access changes.
- Room membership changes.
- Meeting creation.
- Meeting token issuance.
- Guest meeting access creation or revocation.
- Account suspension or restoration.
- Backup and restore actions where the portal records them.

Audit event requirements:

- `actor_user_id` should be set for administrator or user actions where available.
- `target_user_id` should be set when a user is affected.
- `entity_type` and `entity_id` should identify the main resource.
- `scope_group_id` should be set for group-scoped actions where available.
- `metadata` should contain minimal structured details needed for review.
- Secrets, raw tokens, password material, JWT bodies, session cookies, and message bodies must not be stored in audit metadata.

## 12. Migration Strategy

Migration policy:

- Use ordered SQL migration files in `portal/migrations/`.
- Keep migrations idempotent where practical.
- Do not include real users, real parishes, real invites, real rooms, or real secrets in migrations.
- Add schema changes in small reviewed migrations.
- Back up PostgreSQL before production migrations.
- Test migrations against disposable data before production.
- Keep public registration disabled through all migrations.
- Keep open federation disabled unless a later approved feature enables it.
- Preserve audit history during schema changes.

Current migration sequence:

| Migration | Purpose |
| --------- | ------- |
| `001_initial_schema.sql` | Initial portal schema for users, groups, roles, invites, verification, rooms, and audit events. |
| `002_invite_workflow.sql` | Adds reusable invite and use count fields. |
| `003_manual_verification.sql` | Restricts verification types and requires admin decision actor. |
| `004_room_access_model.sql` | Updates room privacy scopes and adds room creator. |
| `005_jitsi_meeting_access.sql` | Adds meeting, guest, and token issuance records. |

Future migrations should include a rollback note, manual validation commands, and expected impact on existing data.

## 13. Rollback Plan

Database rollback must preserve trust records and avoid silent data loss.

Rollback process:

1. Stop portal writes if a migration or schema change is unsafe.
2. Preserve the current database state for review.
3. Identify the last known-good backup and migration version.
4. Restore to a disposable environment first where possible.
5. Verify users, groups, roles, invites, verification records, rooms, meetings, and audit events.
6. Restore production only after the backup passes checks.
7. Confirm public registration remains disabled.
8. Confirm federation remains disabled.
9. Confirm Jitsi authentication remains enabled.
10. Confirm admin access and audit event creation still work.
11. Record the rollback action in operator notes or audit records where supported.

Do not roll back by deleting audit events, verification decisions, role assignments, or room records unless a reviewed retention or data repair procedure explicitly requires it.
