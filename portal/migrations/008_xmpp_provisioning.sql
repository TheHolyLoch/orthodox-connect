-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/008_xmpp_provisioning.sql

ALTER TABLE users
	ADD COLUMN IF NOT EXISTS xmpp_provisioning_status text NOT NULL DEFAULT 'not_provisioned'
		CHECK (xmpp_provisioning_status IN ('not_provisioned', 'provisioned', 'failed', 'disabled')),
	ADD COLUMN IF NOT EXISTS xmpp_provisioning_error text,
	ADD COLUMN IF NOT EXISTS xmpp_provisioned_at timestamptz,
	ADD COLUMN IF NOT EXISTS xmpp_disabled_at timestamptz;

CREATE INDEX IF NOT EXISTS idx_users_xmpp_provisioning_status ON users(xmpp_provisioning_status);
