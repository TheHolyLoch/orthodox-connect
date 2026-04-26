-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/001_initial_schema.sql

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	xmpp_jid text UNIQUE,
	display_name text NOT NULL,
	email text UNIQUE,
	status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'denied', 'suspended', 'disabled')),
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE groups (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	parent_group_id uuid REFERENCES groups(id) ON DELETE SET NULL,
	name text NOT NULL,
	slug text NOT NULL UNIQUE,
	group_type text NOT NULL CHECK (group_type IN ('parish', 'monastery', 'mission', 'ministry', 'shared', 'administrative')),
	description text,
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE group_memberships (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	group_id uuid NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
	user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	status text NOT NULL DEFAULT 'pending' CHECK (status IN ('invited', 'pending', 'active', 'suspended', 'removed')),
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now(),
	UNIQUE (group_id, user_id)
);

CREATE TABLE roles (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	name text NOT NULL UNIQUE,
	description text,
	created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE user_roles (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	role_id uuid NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
	group_id uuid REFERENCES groups(id) ON DELETE CASCADE,
	granted_by_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	granted_at timestamptz NOT NULL DEFAULT now(),
	revoked_at timestamptz,
	UNIQUE (user_id, role_id, group_id)
);

CREATE TABLE invites (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	token_hash text NOT NULL UNIQUE,
	created_by_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	group_id uuid REFERENCES groups(id) ON DELETE SET NULL,
	expected_role_id uuid REFERENCES roles(id) ON DELETE SET NULL,
	status text NOT NULL DEFAULT 'unused' CHECK (status IN ('unused', 'accepted', 'expired', 'revoked')),
	expires_at timestamptz NOT NULL,
	accepted_by_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	accepted_at timestamptz,
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE verification_requests (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	group_id uuid REFERENCES groups(id) ON DELETE SET NULL,
	request_type text NOT NULL CHECK (request_type IN ('member', 'clergy', 'monastic')),
	status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'denied', 'cancelled')),
	note text,
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE verification_decisions (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	verification_request_id uuid NOT NULL REFERENCES verification_requests(id) ON DELETE CASCADE,
	decided_by_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	decision text NOT NULL CHECK (decision IN ('approved', 'denied', 'revoked')),
	reason text,
	decided_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE rooms (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	group_id uuid REFERENCES groups(id) ON DELETE SET NULL,
	name text NOT NULL,
	slug text NOT NULL UNIQUE,
	xmpp_room_jid text UNIQUE,
	privacy_level text NOT NULL DEFAULT 'members' CHECK (privacy_level IN ('public-local', 'members', 'restricted', 'announcement', 'shared', 'private')),
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE room_memberships (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	room_id uuid NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
	user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
	role text NOT NULL DEFAULT 'member' CHECK (role IN ('member', 'moderator', 'admin')),
	status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'removed')),
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now(),
	UNIQUE (room_id, user_id)
);

CREATE TABLE audit_events (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	actor_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	target_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	entity_type text NOT NULL,
	entity_id uuid,
	action text NOT NULL,
	scope_group_id uuid REFERENCES groups(id) ON DELETE SET NULL,
	metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
	created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_group_memberships_user_id ON group_memberships(user_id);
CREATE INDEX idx_invites_status ON invites(status);
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_verification_requests_user_id ON verification_requests(user_id);
CREATE INDEX idx_room_memberships_user_id ON room_memberships(user_id);
CREATE INDEX idx_audit_events_actor_user_id ON audit_events(actor_user_id);
CREATE INDEX idx_audit_events_created_at ON audit_events(created_at);
