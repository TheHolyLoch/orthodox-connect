# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/verifications.py

import json

from portal.app import db


ROLE_BY_REQUEST_TYPE = {
	'clergy': 'clergy_verified',
	'monastic': 'monastic_verified',
	'parish_admin': 'parish_admin',
}


class VerificationError(Exception):
	'''Base exception for verification workflow failures.'''


class VerificationDecisionError(VerificationError):
	'''Raised when a verification request cannot be decided.'''


class VerificationRequestError(VerificationError):
	'''Raised when a verification request cannot be created.'''


def approve_request(request_id: str, admin_user_id: str, reason: str | None = None) -> dict:
	'''
	Approve a verification request, assign its role, and write audit records.

	:param request_id: Verification request ID
	:param admin_user_id: Admin user ID making the decision
	:param reason: Optional decision reason
	'''

	return decide_request(request_id, admin_user_id, 'approved', reason)


def create_request(user_id: str, request_type: str, group_id: str | None = None, note: str | None = None) -> dict:
	'''
	Create a pending verification request and write an audit record.

	:param user_id: User requesting verification
	:param request_type: Verification type
	:param group_id: Optional group scope
	:param note: Optional request note
	'''

	validate_request_type(request_type)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))

			if not cursor.fetchone():
				raise VerificationRequestError('user not found')

			cursor.execute(
				'''
				INSERT INTO verification_requests (
					user_id,
					group_id,
					request_type,
					note
				)
				VALUES (%s, %s, %s, %s)
				RETURNING
					id,
					user_id,
					group_id,
					request_type,
					status,
					note,
					created_at,
					updated_at
				''',
				(user_id, group_id, request_type, note)
			)
			request = cursor.fetchone()

			cursor.execute(
				'''
				INSERT INTO audit_events (
					actor_user_id,
					target_user_id,
					entity_type,
					entity_id,
					action,
					scope_group_id,
					metadata
				)
				VALUES (%s, %s, 'verification_request', %s, 'verification_requested', %s, %s::jsonb)
				''',
				(
					user_id,
					user_id,
					request['id'],
					group_id,
					json.dumps({'request_type': request_type})
				)
			)

		connection.commit()

	return request


def decide_request(request_id: str, admin_user_id: str, decision: str, reason: str | None = None) -> dict:
	'''
	Approve or reject a pending verification request.

	:param request_id: Verification request ID
	:param admin_user_id: Admin user ID making the decision
	:param decision: approved or denied
	:param reason: Optional reason
	'''

	if decision not in ('approved', 'denied'):
		raise VerificationDecisionError('decision must be approved or denied')

	if decision == 'denied' and not reason:
		raise VerificationDecisionError('rejected requests require a reason')

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute('SELECT id FROM users WHERE id = %s', (admin_user_id,))

			if not cursor.fetchone():
				raise VerificationDecisionError('admin user not found')

			cursor.execute(
				'''
				SELECT
					id,
					user_id,
					group_id,
					request_type,
					status
				FROM verification_requests
				WHERE id = %s
				FOR UPDATE
				''',
				(request_id,)
			)
			request = cursor.fetchone()

			if not request:
				raise VerificationDecisionError('verification request not found')

			if request['status'] != 'pending':
				raise VerificationDecisionError('verification request is already decided')

			cursor.execute(
				'''
				UPDATE verification_requests
				SET
					status = %s,
					updated_at = now()
				WHERE id = %s
				RETURNING
					id,
					user_id,
					group_id,
					request_type,
					status,
					note,
					created_at,
					updated_at
				''',
				(decision, request_id)
			)
			updated_request = cursor.fetchone()

			cursor.execute(
				'''
				INSERT INTO verification_decisions (
					verification_request_id,
					decided_by_user_id,
					decision,
					reason
				)
				VALUES (%s, %s, %s, %s)
				RETURNING
					id,
					verification_request_id,
					decided_by_user_id,
					decision,
					reason,
					decided_at
				''',
				(request_id, admin_user_id, decision, reason)
			)
			verification_decision = cursor.fetchone()
			assigned_role          = None

			if decision == 'approved':
				assigned_role = assign_role(cursor, updated_request, admin_user_id)

			cursor.execute(
				'''
				INSERT INTO audit_events (
					actor_user_id,
					target_user_id,
					entity_type,
					entity_id,
					action,
					scope_group_id,
					metadata
				)
				VALUES (%s, %s, 'verification_request', %s, %s, %s, %s::jsonb)
				''',
				(
					admin_user_id,
					updated_request['user_id'],
					updated_request['id'],
					verification_action(decision),
					updated_request['group_id'],
					json.dumps({
						'decision_id': str(verification_decision['id']),
						'reason': reason,
						'request_type': updated_request['request_type'],
					})
				)
			)

		connection.commit()

	return {
		'assigned_role': assigned_role,
		'decision': verification_decision,
		'request': updated_request,
	}


def assign_role(cursor, request: dict, admin_user_id: str) -> dict:
	'''
	Assign the role that matches an approved verification request.

	:param cursor: Open database cursor
	:param request: Approved verification request
	:param admin_user_id: Admin user ID assigning the role
	'''

	role_name = ROLE_BY_REQUEST_TYPE[request['request_type']]

	cursor.execute(
		'''
		INSERT INTO roles (
			name,
			description
		)
		VALUES (%s, %s)
		ON CONFLICT (name) DO UPDATE
		SET description = EXCLUDED.description
		RETURNING id, name, description, created_at
		''',
		(role_name, role_description(role_name))
	)
	role = cursor.fetchone()

	cursor.execute(
		'''
		INSERT INTO user_roles (
			user_id,
			role_id,
			group_id,
			granted_by_user_id
		)
		VALUES (%s, %s, %s, %s)
		ON CONFLICT (user_id, role_id, group_id) DO UPDATE
		SET
			granted_by_user_id = EXCLUDED.granted_by_user_id,
			granted_at = now(),
			revoked_at = NULL
		RETURNING
			id,
			user_id,
			role_id,
			group_id,
			granted_by_user_id,
			granted_at,
			revoked_at
		''',
		(request['user_id'], role['id'], request['group_id'], admin_user_id)
	)
	user_role = cursor.fetchone()

	return {'role': role, 'user_role': user_role}


def list_requests(status: str | None = None, user_id: str | None = None) -> list[dict]:
	'''
	Return verification request state with the latest decision data.

	:param status: Optional request status filter
	:param user_id: Optional user ID filter
	'''

	query = '''
		SELECT
			vr.id,
			vr.user_id,
			vr.group_id,
			vr.request_type,
			vr.status,
			vr.note,
			vr.created_at,
			vr.updated_at,
			vd.decided_by_user_id,
			vd.decision,
			vd.reason,
			vd.decided_at
		FROM verification_requests vr
		LEFT JOIN LATERAL (
			SELECT
				decided_by_user_id,
				decision,
				reason,
				decided_at
			FROM verification_decisions
			WHERE verification_request_id = vr.id
			ORDER BY decided_at DESC
			LIMIT 1
		) vd ON true
		WHERE (%s::text IS NULL OR vr.status = %s)
			AND (%s::uuid IS NULL OR vr.user_id = %s::uuid)
		ORDER BY vr.created_at DESC
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(query, (status, status, user_id, user_id))

			return cursor.fetchall()


def reject_request(request_id: str, admin_user_id: str, reason: str) -> dict:
	'''
	Reject a verification request with a reason.

	:param request_id: Verification request ID
	:param admin_user_id: Admin user ID making the decision
	:param reason: Rejection reason
	'''

	return decide_request(request_id, admin_user_id, 'denied', reason)


def role_description(role_name: str) -> str:
	'''
	Return a short role description.

	:param role_name: Role name
	'''

	descriptions = {
		'clergy_verified': 'Verified clergy status granted through manual review.',
		'monastic_verified': 'Verified monastic status granted through manual review.',
		'parish_admin': 'Local administrator for invites, verification, roles, and rooms.',
	}

	return descriptions[role_name]


def validate_request_type(request_type: str):
	'''
	Validate a supported verification type.

	:param request_type: Verification request type
	'''

	if request_type not in ROLE_BY_REQUEST_TYPE:
		raise VerificationRequestError('unsupported verification type')


def verification_action(decision: str) -> str:
	'''
	Return the audit action for a decision value.

	:param decision: Verification decision
	'''

	if decision == 'approved':
		return 'verification_approved'

	return 'verification_rejected'
