-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/006_portal_authentication.sql

ALTER TABLE users
	ADD COLUMN password_hash text,
	ADD COLUMN last_login_at timestamptz;

CREATE INDEX idx_users_email ON users(email);
