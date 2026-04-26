-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/002_invite_workflow.sql

ALTER TABLE invites
	ADD COLUMN reusable boolean NOT NULL DEFAULT false,
	ADD COLUMN use_count integer NOT NULL DEFAULT 0 CHECK (use_count >= 0);

CREATE INDEX idx_invites_expires_at ON invites(expires_at);
CREATE INDEX idx_invites_reusable ON invites(reusable);
