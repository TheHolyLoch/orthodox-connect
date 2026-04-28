# Orthodox Connect API Design

## API Goals

The portal API should expose the portal control plane in a predictable, auditable, and role-aware way.

Goals:

- Support the portal web UI without duplicating trust logic in templates.
- Keep registration invite-only.
- Keep clergy, monastic, parish admin, diocesan admin, and platform admin status administrator-controlled.
- Keep room and meeting access derived from roles, groups, explicit membership, and suspension state.
- Record audit events for trust and access decisions.
- Avoid exposing internal service details, secrets, raw tokens, or private notes.
- Keep the API small enough for local operators to review.
- Provide stable contracts for future mobile or integration work after authentication and permissions are reviewed.

The API should not become a public social network interface or a bypass around portal policy.

## Authentication Model

Portal authentication should be account-based and tied to portal users stored in PostgreSQL.

Baseline requirements:

- Users authenticate before accessing private API resources.
- Public registration remains unavailable.
- Invite redemption is the only account creation path.
- Suspended users cannot use authenticated API endpoints.
- Admin endpoints require approved admin roles.
- Privileged actions require explicit role checks at the API layer.
- Authentication failures are logged as security events without storing passwords or session cookies.

Future native clients or integrations must use the same portal identity and permission checks. They must not authenticate directly to PostgreSQL, Prosody internals, Jitsi internals, or Docker services.

## Session vs Token Approach

The portal web UI should use secure server-managed sessions by default.

Preferred session model:

- HTTP-only secure cookies.
- SameSite protection where compatible with the deployment.
- CSRF protection for browser form and state-changing API requests.
- Shorter session lifetime for administrator accounts.
- Session invalidation when an account is suspended or disabled.
- No session cookie values in logs.

Token use should be limited and purpose-specific.

Allowed token types:

| Token Type       | Use Case                                 | Notes |
| ---------------- | ---------------------------------------- | ----- |
| Invite token     | Invite redemption only.                  | Must expire and must not be logged. |
| Recovery token   | Future account recovery only.            | Must expire and require stronger review for privileged roles. |
| Jitsi JWT        | Meeting access only.                     | Issued only after portal policy checks. |
| API token        | Future service integration only.         | Requires a separate review before implementation. |

The MVP API design should not require long-lived bearer tokens for normal browser use.

## Endpoint Categories

API paths should be grouped by category under a versioned prefix such as `/api/v1/`. This document defines categories and responsibilities only. Exact endpoint paths should be added when API implementation begins.

### Auth

Auth covers sign-in, sign-out, session status, invite redemption, and future recovery.

Responsibilities:

- Authenticate portal users.
- End authenticated sessions.
- Report current session user and role state.
- Redeem valid invites.
- Reject expired, revoked, and already-used single-use invites.
- Keep public registration unavailable.

Auth must not allow users to self-assign roles, verification status, group membership, room membership, or meeting creation rights.

### Users

Users covers account records and account state.

Responsibilities:

- List users visible to the authenticated administrator's scope.
- Show user details allowed by the requester role.
- Update limited account fields where policy allows.
- Suspend or restore accounts through administrator action.
- Expose current user's own status without exposing admin-only notes.

User responses must not include password hashes, session secrets, invite tokens, recovery tokens, private verification notes, or raw Jitsi tokens.

### Roles

Roles covers role definitions and user role assignments.

Responsibilities:

- List defined roles.
- Show which roles are assigned to a user where the requester has permission.
- Assign or remove roles through administrator action.
- Keep privileged roles administrator-controlled.
- Prevent users from assigning roles to themselves.

Role changes must create audit events.

### Groups

Groups covers parishes, monasteries, ministries, and other local membership groups.

Responsibilities:

- List groups visible to the requester.
- Show group membership where permitted.
- Add or remove users from groups through administrator action.
- Preserve group scope for rooms, verification, and moderation.

Group membership changes must be explicit and audited.

### Invites

Invites covers invite creation, listing, revocation, and redemption state.

Responsibilities:

- Create invites through authorized administrators.
- List invite status without exposing raw tokens after creation.
- Revoke invites.
- Show expiry, creator, reusable status, and redemption state.
- Support single-use invites by default.
- Support reusable invites only when explicitly marked.

Invite creation, revocation, and redemption must create audit events.

### Verification

Verification covers requests and decisions for trusted roles.

Supported request types:

- `clergy`
- `monastic`
- `parish_admin`

Responsibilities:

- Let users submit verification requests.
- Let authorized administrators list pending requests.
- Let authorized administrators approve or reject requests.
- Store rejection reasons.
- Assign the matching role for approved requests.
- Keep verification decisions tied to the deciding administrator.

Verification request creation, approval, and rejection must create audit events.

### Rooms

Rooms covers room definitions, room policy, access checks, and room membership records.

Supported scopes:

- `public_to_members`
- `group_only`
- `clergy_only`
- `monastic_only`
- `admin_only`
- `invite_only`

Responsibilities:

- List rooms available to the requester.
- Let administrators define rooms and policy.
- Calculate whether a user may access a room.
- Create room membership records only when access rules allow it.
- Prevent suspended users from joining rooms.
- Keep Prosody synchronization separate until implemented.

Room creation, policy changes, access changes, and membership changes must create audit events.

### Meetings

Meetings covers Jitsi meeting records, creation policy, guest access, and token issuance.

Responsibilities:

- Let approved creator roles create official meetings.
- Deny public anonymous meeting creation.
- Issue Jitsi JWTs only after portal access checks.
- Issue guest access only where explicitly allowed.
- Keep meeting names from granting access by themselves.
- Expire meeting tokens based on policy.

Meeting creation and token issuance must create audit events.

### Audit

Audit covers read access to trust and access decision records.

Responsibilities:

- List audit events visible to authorized administrators.
- Filter by actor, target, event type, resource type, and time range where implemented.
- Preserve append-only behavior from the application perspective.
- Hide audit details from ordinary users except their own limited account status where policy allows.

Audit APIs must not allow ordinary edit or delete operations on audit records.

## Request and Response Format

The API should use JSON over HTTPS.

Request rules:

- Use `Content-Type: application/json` for JSON requests.
- Use UTF-8.
- Use stable snake_case field names.
- Send dates and times as ISO 8601 strings in UTC.
- Send IDs as strings unless the implementation standardizes numeric IDs.
- Avoid request bodies for simple list filters when query parameters are enough.
- Do not send passwords, tokens, or secrets in query strings.

Successful response envelope:

```json
{
	"data": {},
	"meta": {
		"request_id": "req_example"
	}
}
```

List response envelope:

```json
{
	"data": [],
	"pagination": {
		"limit": 50,
		"next_cursor": "cursor_example",
		"previous_cursor": null
	},
	"meta": {
		"request_id": "req_example"
	}
}
```

Responses should omit fields the requester cannot see instead of returning private values as `null`.

## Error Handling Format

Errors should be JSON and should not expose stack traces, SQL errors, internal hostnames, raw tokens, or service secrets.

Error response envelope:

```json
{
	"error": {
		"code": "forbidden",
		"message": "You do not have permission to perform this action.",
		"details": {}
	},
	"meta": {
		"request_id": "req_example"
	}
}
```

Recommended error codes:

| HTTP Status | API Code               | Use Case |
| ----------- | ---------------------- | -------- |
| 400         | `bad_request`          | Invalid syntax or invalid field value. |
| 401         | `unauthenticated`      | No valid session or credential. |
| 403         | `forbidden`            | Authenticated but not allowed. |
| 404         | `not_found`            | Resource missing or hidden from requester. |
| 409         | `conflict`             | State conflict such as already-used invite. |
| 410         | `expired`              | Expired invite, token, or link. |
| 422         | `validation_failed`    | Well-formed request with failed validation. |
| 429         | `rate_limited`         | Rate limit exceeded. |
| 500         | `internal_error`       | Server error with no private details. |
| 503         | `service_unavailable`  | Required dependency unavailable. |

Authorization-sensitive lookups may return `404` instead of `403` when revealing existence would expose private rooms, users, invites, or meetings.

## Pagination Model

List endpoints should use cursor pagination by default.

Pagination rules:

- Default `limit` should be conservative.
- Maximum `limit` should be enforced by the server.
- Cursor values should be opaque to clients.
- Sort order should be stable.
- Audit event lists should default to newest first.
- User, group, role, invite, verification, room, and meeting lists should document their default sort before implementation.

Offset pagination may be used only for small admin-only lists where consistency risk is acceptable.

## Rate Limiting Strategy

Rate limiting should protect the invite-only model and administrator workflows without blocking normal parish use.

Rate limit by:

- Account identifier where authenticated.
- Session where authenticated.
- IP address or route metadata where useful.
- Invite token for redemption attempts.
- Username or email identifier for login attempts when login exists.
- Meeting token issuance target.

Priority routes for limits:

- Sign-in.
- Invite redemption.
- Recovery requests when implemented.
- Verification request creation.
- Meeting token issuance.
- Admin actions that can create many records.

Rate limits should fail closed with `429` and should create security or audit records where useful. Rate limit responses must not reveal whether an account, invite, or recovery token exists.

## Audit Logging Integration

The API should write audit records for trust and access decisions.

Audited API actions:

- Invite created.
- Invite revoked.
- Invite redeemed.
- User suspended.
- User restored.
- Role assigned.
- Role removed.
- Group membership added.
- Group membership removed.
- Verification request created.
- Verification request approved.
- Verification request rejected.
- Room created.
- Room policy changed.
- Room membership added.
- Room membership removed.
- Meeting created.
- Meeting token issued.
- Guest meeting token issued.

Audit event fields should include:

- Actor user ID.
- Target resource ID.
- Resource type.
- Event type.
- Scope.
- Timestamp.
- Request ID.
- Reason or note where needed.
- Minimal route or source metadata if policy allows it.

Audit records should never store passwords, invite tokens, recovery tokens, JWT bodies, session cookies, full request bodies, private message content, or private pastoral notes.

## Permission Checks

Permission checks must happen server-side for every API request.

Rules:

- UI visibility is not an authorization control.
- Admin roles must be verified from portal data on each privileged action.
- Suspended users are denied authenticated access.
- Users cannot approve their own verification requests.
- Users cannot grant roles to themselves.
- Users cannot create official meetings unless their roles are approved for meeting creation.
- Users cannot access rooms unless policy allows it.
- Group-scoped admins can act only within their allowed group scope.
- Platform-level actions require platform-level roles.

Permission checks should use shared portal policy functions when implementation begins, so the API, admin UI, CLI, and future integrations do not drift.

## Internal vs External API Distinction

The first API should be internal to the portal web application and trusted local deployment.

Internal API:

- Used by the portal UI.
- Uses browser sessions.
- Exposed only through the portal hostname.
- Uses the same Caddy HTTPS route as the portal.
- Does not expose service-to-service secrets to browsers.
- Does not allow direct database, Prosody admin, Jitsi internal, Docker, or host access.

External API:

- Future scope.
- Requires separate review before enabling.
- Requires scoped tokens or another reviewed authentication model.
- Requires stricter rate limits, audit logging, documentation, and operator controls.
- Must not be enabled by default.

Native mobile clients should use the portal API only after account provisioning, session or token policy, push notification policy, and client behavior are reviewed.

## Versioning Strategy

API versioning should be explicit.

Rules:

- Use a URL prefix such as `/api/v1/`.
- Keep breaking changes out of an existing version.
- Add new optional fields before replacing existing fields.
- Do not change enum meanings without a new version or migration note.
- Keep old versions only as long as the portal UI or supported clients need them.
- Document deprecation dates before removing a version.

The first implemented API should be treated as private to the portal UI until it is stable enough for external clients.

## Rollback Plan

API rollback must protect trust records and avoid partial state changes.

Rollback steps:

1. Disable or revert the faulty API route, handler, or client call.
2. Confirm portal admin access still works.
3. Confirm public registration remains unavailable.
4. Confirm invite redemption still rejects expired, revoked, and already-used single-use invites.
5. Confirm verification decisions still require administrator roles.
6. Confirm room access checks still deny unauthorized and suspended users.
7. Confirm Jitsi meeting creation and token issuance remain role-gated.
8. Preserve audit events created before rollback.
9. Add corrective audit events for any manual repair.
10. Rotate secrets if tokens, cookies, JWTs, or session data were exposed.
11. Restore from backup only if data integrity cannot be repaired safely.

Rollback must not delete users, roles, groups, invites, verification records, rooms, meetings, audit events, backups, Prosody data, Jitsi state, or unrelated service configuration.
