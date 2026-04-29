-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/009_muc_room_provisioning.sql

ALTER TABLE rooms
	ADD COLUMN IF NOT EXISTS muc_provisioning_status text NOT NULL DEFAULT 'not_provisioned'
		CHECK (muc_provisioning_status IN ('not_provisioned', 'provisioned', 'failed')),
	ADD COLUMN IF NOT EXISTS muc_provisioning_error text,
	ADD COLUMN IF NOT EXISTS muc_provisioned_at timestamptz;

CREATE INDEX IF NOT EXISTS idx_rooms_muc_provisioning_status ON rooms(muc_provisioning_status);
