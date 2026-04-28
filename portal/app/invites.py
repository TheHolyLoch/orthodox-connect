# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/invites.py

import hashlib
import json
import secrets

from datetime import datetime, timezone

from portal.app import auth, config, db, rooms


class InviteError(Exception):
	'''Base exception for invite workflow failures.'''


class InviteExpiredError(InviteError):
	'''Raised when an invite has expired.'''


class InviteInputError(InviteError):
	'''Raised when invite input is invalid.'''


class InviteRedeemedError(InviteError):
	'''Raised when a single-use invite has already been redeemed.'''


class InviteRevokedError(InviteError):
	'''Raised when an invite has been revoked.'''


class InviteUnknownError(InviteError):
	'''Raised when an invite token cannot be found.'''


class InviteUnauthorizedError(InviteError):
	'''Raised when an actor cannot manage invites.'''


def create_invite(
	created_by_user_id: str,
	expires_at: datetime,
	expected_role_id: str | None = None,
	group_id: str | None = None,
	max_uses: int = 1,
	reusable: bool = False
) -> dict:
	'''
	Create an invite and return the stored invite fields plus the one-time token.

	:param created_by_user_id: User ID that created the invite
	:param expires_at: Expiration timestamp
	:param expected_role_id: Optional expected role ID
	:param group_id: Optional group scope ID
	:param max_uses: Maximum number of successful redemptions
	:param reusable: Whether the invite may be redeemed more than once
	'''

	validate_max_uses(max_uses)
	token      = secrets.token_urlsafe(config.invite_token_bytes())
	token_hash = hash_token(token)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, created_by_user_id)
			cursor.execute(
				'''
				INSERT INTO invites (
					token_hash,
					created_by_user_id,
					group_id,
					expected_role_id,
					expires_at,
					max_uses,
					reusable
				)
				VALUES (%s, %s, %s, %s, %s, %s, %s)
				RETURNING
					id,
					created_by_user_id,
					group_id,
					expected_role_id,
					status,
					expires_at,
					max_uses,
					reusable,
					use_count,
					used_at,
					revoked_at,
					created_at,
					updated_at
				''',
				(token_hash, created_by_user_id, group_id, expected_role_id, expires_at, max_uses, reusable)
			)
			invite = cursor.fetchone()

			cursor.execute(
				'''
				INSERT INTO audit_events (
					actor_user_id,
					entity_type,
					entity_id,
					action,
					scope_group_id,
					metadata
				)
				VALUES (%s, 'invite', %s, 'invite_created', %s, %s::jsonb)
				''',
				(
					created_by_user_id,
					invite['id'],
					group_id,
					json.dumps({'expires_at': expires_at.isoformat(), 'max_uses': max_uses, 'reusable': reusable})
				)
			)

		connection.commit()

	invite['token'] = token

	return invite


def hash_token(token: str) -> str:
	'''
	Hash an invite token for database storage.

	:param token: Raw invite token
	'''

	return hashlib.sha256(token.encode('utf-8')).hexdigest()


def list_invites() -> list[dict]:
	'''
	Return invite records without token hashes.
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT
					id,
					created_by_user_id,
					group_id,
					expected_role_id,
					status,
					expires_at,
					max_uses,
					reusable,
					use_count,
					accepted_by_user_id,
					accepted_at,
					used_at,
					revoked_at,
					created_at,
					updated_at
				FROM invites
				ORDER BY created_at DESC
				'''
			)

			return cursor.fetchall()


def redeem_invite(token: str, display_name: str, email: str, password: str) -> dict:
	'''
	Redeem a valid invite and create a pending user.

	:param token: Raw invite token
	:param display_name: Display name for the pending account
	:param email: Account email
	:param password: Plain account password
	'''

	display_name = display_name.strip()
	email        = auth.normalize_email(email)
	token        = token.strip()

	if not token:
		raise InviteUnknownError('invite token not found')

	if not display_name:
		raise InviteInputError('display name is required')

	if not email:
		raise InviteInputError('email is required')

	if not password:
		raise InviteInputError('password is required')

	token_hash = hash_token(token)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT
					id,
					created_by_user_id,
					group_id,
					expected_role_id,
					status,
					expires_at,
					reusable,
					use_count,
					max_uses,
					revoked_at
				FROM invites
				WHERE token_hash = %s
				FOR UPDATE
				''',
				(token_hash,)
			)
			invite = cursor.fetchone()

			if not invite:
				raise InviteUnknownError('invite token not found')

			if invite['status'] == 'revoked' or invite['revoked_at']:
				raise InviteRevokedError('invite has been revoked')

			if invite['expires_at'] <= datetime.now(timezone.utc):
				if invite['status'] == 'unused':
					cursor.execute(
						"UPDATE invites SET status = 'expired', updated_at = now() WHERE id = %s",
						(invite['id'],)
					)
					connection.commit()

				raise InviteExpiredError('invite has expired')

			if invite['status'] == 'accepted' or invite['use_count'] >= invite['max_uses']:
				raise InviteRedeemedError('invite has already been redeemed')

			cursor.execute('SELECT id FROM users WHERE email = %s', (email,))

			if cursor.fetchone():
				raise InviteInputError('email already has an account')

			cursor.execute(
				'''
				INSERT INTO users (
					display_name,
					email,
					password_hash,
					status
				)
				VALUES (%s, %s, %s, 'pending')
				RETURNING
					id,
					xmpp_jid,
					display_name,
					email,
					status,
					created_at,
					updated_at
				''',
				(display_name, email, auth.hash_password(password))
			)
			user = cursor.fetchone()

			if invite['group_id']:
				cursor.execute(
					'''
					INSERT INTO group_memberships (
						group_id,
						user_id,
						status
					)
					VALUES (%s, %s, 'pending')
					ON CONFLICT (group_id, user_id) DO NOTHING
					''',
					(invite['group_id'], user['id'])
				)

			cursor.execute(
				'''
				UPDATE invites
				SET
					status = CASE WHEN use_count + 1 >= max_uses THEN 'accepted' ELSE status END,
					accepted_by_user_id = COALESCE(accepted_by_user_id, %s),
					accepted_at = COALESCE(accepted_at, now()),
					use_count = use_count + 1,
					used_at = now(),
					updated_at = now()
				WHERE id = %s
				RETURNING
					id,
					status,
					max_uses,
					reusable,
					use_count,
					accepted_by_user_id,
					accepted_at,
					used_at,
					revoked_at
				''',
				(user['id'], invite['id'])
			)
			updated_invite = cursor.fetchone()

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
				VALUES (%s, %s, 'invite', %s, 'invite_redeemed', %s, %s::jsonb)
				''',
				(
					user['id'],
					user['id'],
					invite['id'],
					invite['group_id'],
					json.dumps({
						'created_by_user_id': str(invite['created_by_user_id']) if invite['created_by_user_id'] else None,
						'max_uses': invite['max_uses'],
						'reusable': invite['reusable']
					})
				)
			)

		connection.commit()

	return {'invite': updated_invite, 'user': user}


def revoke_invite(invite_id: str, actor_user_id: str) -> dict:
	'''
	Revoke an invite and record an audit event.

	:param invite_id: Invite ID to revoke
	:param actor_user_id: User ID performing the revocation
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, actor_user_id)
			cursor.execute(
				'''
				UPDATE invites
				SET
					status = 'revoked',
					revoked_at = now(),
					updated_at = now()
				WHERE id = %s
					AND status NOT IN ('accepted', 'expired', 'revoked')
				RETURNING
					id,
					created_by_user_id,
					group_id,
					expected_role_id,
					status,
					expires_at,
					max_uses,
					reusable,
					use_count,
					used_at,
					revoked_at,
					created_at,
					updated_at
				''',
				(invite_id,)
			)
			invite = cursor.fetchone()

			if not invite:
				raise InviteUnknownError('active invite not found')

			cursor.execute(
				'''
				INSERT INTO audit_events (
					actor_user_id,
					entity_type,
					entity_id,
					action,
					scope_group_id,
					metadata
				)
				VALUES (%s, 'invite', %s, 'invite_revoked', %s, %s::jsonb)
				''',
				(actor_user_id, invite['id'], invite['group_id'], json.dumps({'status': invite['status']}))
			)

		connection.commit()

	return invite


def require_admin(cursor, actor_user_id: str):
	'''
	Require an approved admin actor for invite management.

	:param cursor: Open database cursor
	:param actor_user_id: Acting user ID
	'''

	user = rooms.fetch_user(cursor, actor_user_id)

	if not user or user['status'] != 'approved':
		raise InviteUnauthorizedError('admin user is required')

	if not rooms.has_any_scoped_role(cursor, actor_user_id, rooms.ADMIN_ROLES):
		raise InviteUnauthorizedError('admin role is required')


def validate_max_uses(max_uses: int):
	'''
	Validate invite maximum use count.

	:param max_uses: Maximum redemption count
	'''

	if max_uses < 1:
		raise InviteInputError('max uses must be at least 1')
