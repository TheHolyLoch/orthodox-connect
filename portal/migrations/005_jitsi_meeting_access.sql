-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/005_jitsi_meeting_access.sql

CREATE TABLE meetings (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	room_id uuid REFERENCES rooms(id) ON DELETE SET NULL,
	created_by_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	name text NOT NULL,
	slug text NOT NULL UNIQUE,
	jitsi_room_name text NOT NULL UNIQUE,
	allow_guests boolean NOT NULL DEFAULT false,
	status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'closed', 'cancelled')),
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE meeting_guests (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	meeting_id uuid NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
	display_name text NOT NULL,
	email text,
	status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked')),
	expires_at timestamptz NOT NULL,
	created_by_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	created_at timestamptz NOT NULL DEFAULT now(),
	updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE meeting_token_issuances (
	id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
	meeting_id uuid NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
	user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	guest_id uuid REFERENCES meeting_guests(id) ON DELETE SET NULL,
	issued_by_user_id uuid REFERENCES users(id) ON DELETE SET NULL,
	token_id text NOT NULL UNIQUE,
	expires_at timestamptz NOT NULL,
	created_at timestamptz NOT NULL,
	CHECK (
		(user_id IS NOT NULL AND guest_id IS NULL)
		OR (user_id IS NULL AND guest_id IS NOT NULL)
	)
);

CREATE INDEX idx_meetings_room_id ON meetings(room_id);
CREATE INDEX idx_meetings_status ON meetings(status);
CREATE INDEX idx_meeting_guests_meeting_id ON meeting_guests(meeting_id);
CREATE INDEX idx_meeting_guests_status ON meeting_guests(status);
CREATE INDEX idx_meeting_token_issuances_meeting_id ON meeting_token_issuances(meeting_id);
CREATE INDEX idx_meeting_token_issuances_user_id ON meeting_token_issuances(user_id);
CREATE INDEX idx_meeting_token_issuances_guest_id ON meeting_token_issuances(guest_id);
