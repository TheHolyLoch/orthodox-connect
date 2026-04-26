-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/004_room_access_model.sql

ALTER TABLE rooms
	ADD COLUMN created_by_user_id uuid REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE rooms
	DROP CONSTRAINT rooms_privacy_level_check,
	ALTER COLUMN privacy_level SET DEFAULT 'public_to_members',
	ADD CONSTRAINT rooms_privacy_level_check
		CHECK (privacy_level IN ('public_to_members', 'group_only', 'clergy_only', 'monastic_only', 'admin_only', 'invite_only'));

CREATE INDEX idx_rooms_group_id ON rooms(group_id);
CREATE INDEX idx_rooms_privacy_level ON rooms(privacy_level);
CREATE INDEX idx_room_memberships_room_status ON room_memberships(room_id, status);
