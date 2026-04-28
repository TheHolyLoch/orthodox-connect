-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/007_invite_onboarding.sql

ALTER TABLE invites
	ADD COLUMN max_uses integer NOT NULL DEFAULT 1 CHECK (max_uses > 0),
	ADD COLUMN revoked_at timestamptz,
	ADD COLUMN used_at timestamptz;

UPDATE invites
SET
	max_uses = CASE WHEN reusable THEN GREATEST(use_count, 1000000) ELSE 1 END,
	used_at = accepted_at
WHERE used_at IS NULL;

UPDATE invites
SET revoked_at = updated_at
WHERE status = 'revoked'
	AND revoked_at IS NULL;

CREATE INDEX idx_invites_revoked_at ON invites(revoked_at);
CREATE INDEX idx_invites_used_at ON invites(used_at);
