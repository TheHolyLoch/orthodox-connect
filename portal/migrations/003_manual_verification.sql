-- Orthodox Connect - Developed by dgm (dgm@tuta.com)
-- orthodox-connect/portal/migrations/003_manual_verification.sql

ALTER TABLE verification_requests
	DROP CONSTRAINT verification_requests_request_type_check,
	ADD CONSTRAINT verification_requests_request_type_check
		CHECK (request_type IN ('clergy', 'monastic', 'parish_admin'));

ALTER TABLE verification_decisions
	ALTER COLUMN decided_by_user_id SET NOT NULL;

CREATE INDEX idx_verification_requests_status ON verification_requests(status);
CREATE INDEX idx_verification_requests_request_type ON verification_requests(request_type);
CREATE INDEX idx_verification_decisions_decided_by_user_id ON verification_decisions(decided_by_user_id);
