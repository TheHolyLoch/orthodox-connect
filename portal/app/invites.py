# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/invites.py

import hashlib
import json
import secrets

from datetime import datetime, timedelta, timezone

from portal.app import config, db


class InviteError(Exception):
	'''Base exception for invite workflow failures.'''


class InviteExpiredError(InviteError):
	'''Raised when an invite has expired.'''


class InviteRedeemedError(InviteError):
	'''Raised when a single-use invite has already been redeemed.'''


class InviteRevokedError(InviteError):
	'''Raised when an invite has been revoked.'''


class InviteUnknownError(InviteError):
	'''Raised when an invite token cannot be found.'''


def create_invite(
	created_by_user_id: str,
	expires_at: datetime,
	expected_role_id: str | None = None,
	group_id: str | None = None,
	reusable: bool = False
) -> dict:
	'''
	Create an invite and return the stored invite fields plus the one-time token.

	:param created_by_user_id: User ID that created the invite
	:param expires_at: Expiration timestamp
	:param expected_role_id: Optional expected role ID
	:param group_id: Optional group scope ID
	:param reusable: Whether the invite may be redeemed more than once
	'''

	token      = secrets.token_urlsafe(config.invite_token_bytes())
	token_hash = hash_token(token)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				INSERT INTO invites (
					token_hash,
					created_by_user_id,
					group_id,
					expected_role_id,
					expires_at,
					reusable
				)
				VALUES (%s, %s, %s, %s, %s, %s)
				RETURNING
					id,
					created_by_user_id,
					group_id,
					expected_role_id,
					status,
					expires_at,
					reusable,
					use_count,
					created_at,
					updated_at
				''',
				(token_hash, created_by_user_id, group_id, expected_role_id, expires_at, reusable)
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
					json.dumps({'reusable': reusable, 'expires_at': expires_at.isoformat()})
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
					reusable,
					use_count,
					accepted_by_user_id,
					accepted_at,
					created_at,
					updated_at
				FROM invites
				ORDER BY created_at DESC
				'''
			)

			return cursor.fetchall()


def redeem_invite(token: str, display_name: str, email: str | None = None, xmpp_jid: str | None = None) -> dict:
	'''
	Redeem a valid invite and create a pending user.

	:param token: Raw invite token
	:param display_name: Display name for the pending account
	:param email: Optional account email
	:param xmpp_jid: Optional planned XMPP JID
	'''

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
					use_count
				FROM invites
				WHERE token_hash = %s
				FOR UPDATE
				''',
				(token_hash,)
			)
			invite = cursor.fetchone()

			if not invite:
				raise InviteUnknownError('invite token not found')

			if invite['status'] == 'revoked':
				raise InviteRevokedError('invite has been revoked')

			if invite['expires_at'] <= datetime.now(timezone.utc):
				if invite['status'] == 'unused':
					cursor.execute(
						"UPDATE invites SET status = 'expired', updated_at = now() WHERE id = %s",
						(invite['id'],)
					)
					connection.commit()

				raise InviteExpiredError('invite has expired')

			if invite['status'] == 'accepted' and not invite['reusable']:
				raise InviteRedeemedError('invite has already been redeemed')

			cursor.execute(
				'''
				INSERT INTO users (
					xmpp_jid,
					display_name,
					email,
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
				(xmpp_jid, display_name, email)
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
					status = CASE WHEN reusable THEN status ELSE 'accepted' END,
					accepted_by_user_id = %s,
					accepted_at = now(),
					use_count = use_count + 1,
					updated_at = now()
				WHERE id = %s
				RETURNING
					id,
					status,
					reusable,
					use_count,
					accepted_by_user_id,
					accepted_at
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
					invite['created_by_user_id'],
					user['id'],
					invite['id'],
					invite['group_id'],
					json.dumps({'reusable': invite['reusable']})
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
			cursor.execute(
				'''
				UPDATE invites
				SET
					status = 'revoked',
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
					reusable,
					use_count,
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
