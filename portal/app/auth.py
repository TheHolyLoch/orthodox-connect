#!/usr/bin/env python3
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/auth.py

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from portal.app import config, db, rooms


ADMIN_ROLES        = rooms.ADMIN_ROLES
HASH_ALGORITHM    = 'pbkdf2_sha256'
HASH_ITERATIONS   = 260_000
SESSION_COOKIE    = 'orthodox_connect_session'
SESSION_SALT_SIZE = 16


class AuthError(Exception):
	'''Base exception for portal authentication failures.'''


class BootstrapError(AuthError):
	'''Raised when bootstrap admin creation fails.'''


def audit_login(cursor, user_id: str | None, action: str, metadata: dict):
	'''
	Write a login-related audit event.

	:param cursor: Open database cursor
	:param user_id: User ID if known
	:param action: Audit action
	:param metadata: Safe event metadata
	'''

	cursor.execute(
		'''
		INSERT INTO audit_events (
			actor_user_id,
			target_user_id,
			entity_type,
			entity_id,
			action,
			metadata
		)
		VALUES (%s, %s, 'auth', %s, %s, %s::jsonb)
		''',
		(user_id, user_id, user_id, action, json.dumps(metadata))
	)


def bootstrap_admin(email: str, display_name: str, password: str) -> dict:
	'''
	Create or update the initial platform admin account.

	:param email: Admin email address
	:param display_name: Admin display name
	:param password: Admin password
	'''

	email        = normalize_email(email)
	display_name = display_name.strip()

	if not email:
		raise BootstrapError('admin email is required')

	if not display_name:
		raise BootstrapError('admin display name is required')

	if not password:
		raise BootstrapError('admin password is required')

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			role_id = ensure_role(cursor, 'platform_admin', 'Instance-level technical and emergency authority.')

			cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
			user = cursor.fetchone()

			if user:
				user_id = user['id']
				cursor.execute(
					'''
					UPDATE users
					SET
						display_name = %s,
						password_hash = %s,
						status = 'approved',
						updated_at = now()
					WHERE id = %s
					RETURNING id, email, display_name, status
					''',
					(display_name, hash_password(password), user_id)
				)
				admin = cursor.fetchone()
			else:
				cursor.execute(
					'''
					INSERT INTO users (
						display_name,
						email,
						status,
						password_hash
					)
					VALUES (%s, %s, 'approved', %s)
					RETURNING id, email, display_name, status
					''',
					(display_name, email, hash_password(password))
				)
				admin  = cursor.fetchone()
				user_id = admin['id']

			cursor.execute(
				'''
				INSERT INTO user_roles (
					user_id,
					role_id,
					granted_by_user_id
				)
				SELECT %s, %s, %s
				WHERE NOT EXISTS (
					SELECT 1
					FROM user_roles
					WHERE user_id = %s
						AND role_id = %s
						AND group_id IS NULL
						AND revoked_at IS NULL
				)
				''',
				(user_id, role_id, user_id, user_id, role_id)
			)
			audit_login(cursor, str(user_id), 'bootstrap_admin_created', {'email': email})

		connection.commit()

	return admin


def create_session(user_id: str, now: int | None = None) -> str:
	'''
	Create a signed session token for a user.

	:param user_id: User ID
	:param now: Current epoch seconds override
	'''

	now     = now or int(time.time())
	expires = now + config.portal_session_ttl_seconds()
	payload = {
		'expires': expires,
		'nonce': secrets.token_urlsafe(12),
		'user_id': user_id,
	}
	encoded_payload = encode_json(payload)
	signature       = sign_payload(encoded_payload)

	return f'{encoded_payload}.{signature}'


def encode_json(payload: dict) -> str:
	'''
	Return URL-safe base64 JSON.

	:param payload: Payload dictionary
	'''

	raw = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8')

	return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def ensure_role(cursor, name: str, description: str) -> str:
	'''
	Return a role ID, creating the role if needed.

	:param cursor: Open database cursor
	:param name: Role name
	:param description: Role description
	'''

	cursor.execute(
		'''
		INSERT INTO roles (name, description)
		VALUES (%s, %s)
		ON CONFLICT (name) DO UPDATE
		SET description = EXCLUDED.description
		RETURNING id
		''',
		(name, description)
	)

	return cursor.fetchone()['id']


def hash_password(password: str) -> str:
	'''
	Return a salted password hash.

	:param password: Plain password
	'''

	salt   = os.urandom(SESSION_SALT_SIZE)
	digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, HASH_ITERATIONS)

	return ':'.join([
		HASH_ALGORITHM,
		str(HASH_ITERATIONS),
		base64.b64encode(salt).decode('ascii'),
		base64.b64encode(digest).decode('ascii'),
	])


def load_session_user(session_token: str | None) -> dict | None:
	'''
	Return the authenticated admin user for a signed session token.

	:param session_token: Session cookie value
	'''

	payload = verify_session(session_token)

	if not payload:
		return None

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT id, email, display_name, status
				FROM users
				WHERE id = %s
				''',
				(payload['user_id'],)
			)
			user = cursor.fetchone()

			if not user or user['status'] != 'approved':
				return None

			if not rooms.has_any_scoped_role(cursor, payload['user_id'], ADMIN_ROLES):
				return None

			return user


def login(email: str, password: str, remote_addr: str | None = None) -> dict | None:
	'''
	Authenticate a portal admin and return user plus session data.

	:param email: Login email address
	:param password: Plain password
	:param remote_addr: Client address metadata
	'''

	email = normalize_email(email)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT id, email, display_name, status, password_hash
				FROM users
				WHERE email = %s
				''',
				(email,)
			)
			user = cursor.fetchone()

			if not user or not user['password_hash'] or not verify_password(password, user['password_hash']):
				audit_login(cursor, str(user['id']) if user else None, 'admin_login_failed', {'email': email, 'remote_addr': remote_addr or ''})
				connection.commit()

				return None

			if user['status'] != 'approved' or not rooms.has_any_scoped_role(cursor, user['id'], ADMIN_ROLES):
				audit_login(cursor, str(user['id']), 'admin_login_failed', {'email': email, 'remote_addr': remote_addr or '', 'reason': 'not_authorized'})
				connection.commit()

				return None

			cursor.execute('UPDATE users SET last_login_at = now(), updated_at = now() WHERE id = %s', (user['id'],))
			audit_login(cursor, str(user['id']), 'admin_login_success', {'email': email, 'remote_addr': remote_addr or ''})
			connection.commit()

			return {'session': create_session(str(user['id'])), 'user': user}


def normalize_email(email: str) -> str:
	'''
	Return normalized email text.

	:param email: Raw email address
	'''

	return (email or '').strip().lower()


def sign_payload(encoded_payload: str) -> str:
	'''
	Return a URL-safe signature for an encoded payload.

	:param encoded_payload: Base64 payload
	'''

	digest = hmac.new(config.portal_secret_key().encode('utf-8'), encoded_payload.encode('ascii'), hashlib.sha256).digest()

	return base64.urlsafe_b64encode(digest).decode('ascii').rstrip('=')


def verify_password(password: str, stored_hash: str) -> bool:
	'''
	Return whether a password matches a stored hash.

	:param password: Plain password
	:param stored_hash: Stored password hash
	'''

	try:
		algorithm, iterations_raw, salt_raw, digest_raw = stored_hash.split(':', 3)
		iterations = int(iterations_raw)
		salt       = base64.b64decode(salt_raw)
		expected   = base64.b64decode(digest_raw)
	except (ValueError, TypeError):
		return False

	if algorithm != HASH_ALGORITHM:
		return False

	actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)

	return hmac.compare_digest(actual, expected)


def verify_session(session_token: str | None) -> dict | None:
	'''
	Verify a signed session token and return its payload.

	:param session_token: Session cookie value
	'''

	if not session_token or '.' not in session_token:
		return None

	encoded_payload, signature = session_token.rsplit('.', 1)

	if not hmac.compare_digest(signature, sign_payload(encoded_payload)):
		return None

	padding = '=' * (-len(encoded_payload) % 4)

	try:
		payload = json.loads(base64.urlsafe_b64decode((encoded_payload + padding).encode('ascii')))
	except (ValueError, json.JSONDecodeError):
		return None

	if int(payload.get('expires', 0)) < int(time.time()):
		return None

	if not payload.get('user_id'):
		return None

	return payload
