# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/xmpp.py

import json
import re
import urllib.error
import urllib.request

from portal.app import config, db, rooms


ADMIN_ROLES    = rooms.ADMIN_ROLES
RESERVED_NODES = {'admin', 'administrator', 'clergy', 'monastic', 'postmaster', 'prosody', 'root', 'support'}


class XmppProvisioningError(Exception):
	'''Base exception for XMPP provisioning failures.'''


class XmppProvisioningInputError(XmppProvisioningError):
	'''Raised when XMPP provisioning input is invalid.'''


class XmppProvisioningRemoteError(XmppProvisioningError):
	'''Raised when Prosody rejects or fails a provisioning request.'''


class XmppProvisioningUnauthorizedError(XmppProvisioningError):
	'''Raised when the actor cannot provision XMPP users.'''


def build_jid(cursor, user: dict) -> str:
	'''
	Build a unique XMPP JID for a portal user.

	:param cursor: Open database cursor
	:param user: User record
	'''

	if user['xmpp_jid']:
		return user['xmpp_jid']

	local_part = (user['email'] or user['display_name'] or '').split('@', 1)[0].lower()
	node       = re.sub(r'[^a-z0-9_.-]+', '-', local_part).strip('._-')

	if not node or len(node) < 3 or node in RESERVED_NODES:
		node = f'user-{str(user["id"])[:8]}'

	node = node[:48].strip('._-') or f'user-{str(user["id"])[:8]}'
	jid  = f'{node}@{config.xmpp_domain()}'

	cursor.execute('SELECT id FROM users WHERE xmpp_jid = %s AND id != %s', (jid, user['id']))

	if cursor.fetchone():
		jid = f'{node}-{str(user["id"])[:8]}@{config.xmpp_domain()}'

	return jid


def call_prosody(action: str, jid: str, password: str | None = None) -> dict:
	'''
	Send a provisioning request to Prosody.

	:param action: Provisioning action
	:param jid: XMPP JID
	:param password: Optional XMPP password
	'''

	payload = {
		'action': action,
		'jid': jid,
	}

	if password is not None:
		payload['password'] = password

	body    = json.dumps(payload).encode('utf-8')
	request = urllib.request.Request(
		config.xmpp_provisioning_url(),
		data=body,
		headers={
			'Authorization': f'Bearer {config.xmpp_provisioning_token()}',
			'Content-Type': 'application/json',
			'Host': config.xmpp_domain(),
		},
		method='POST'
	)

	try:
		with urllib.request.urlopen(request, timeout=10) as response:
			return json.loads(response.read().decode('utf-8'))
	except urllib.error.HTTPError as error:
		raise XmppProvisioningRemoteError(read_error(error)) from error
	except (OSError, json.JSONDecodeError) as error:
		raise XmppProvisioningRemoteError(str(error)) from error


def disable_user(user_id: str, actor_user_id: str) -> dict:
	'''
	Disable a provisioned XMPP account.

	:param user_id: Portal user ID
	:param actor_user_id: Acting admin user ID
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, actor_user_id)
			user = fetch_user(cursor, user_id)

			if not user:
				raise XmppProvisioningInputError('user not found')

			if not user['xmpp_jid']:
				raise XmppProvisioningInputError('user is not provisioned')

			try:
				call_prosody('disable', user['xmpp_jid'])
			except XmppProvisioningRemoteError as error:
				write_xmpp_audit(cursor, actor_user_id, user_id, 'xmpp_provisioning_failure', {'error': str(error), 'jid': user['xmpp_jid']})
				cursor.execute(
					'''
					UPDATE users
					SET
						xmpp_provisioning_status = 'failed',
						xmpp_provisioning_error = %s,
						updated_at = now()
					WHERE id = %s
					RETURNING id, email, display_name, status, xmpp_jid, xmpp_provisioning_status, xmpp_provisioning_error
					''',
					(str(error), user_id)
				)
				connection.commit()
				raise

			cursor.execute(
				'''
				UPDATE users
				SET
					xmpp_provisioning_status = 'disabled',
					xmpp_provisioning_error = NULL,
					xmpp_disabled_at = now(),
					updated_at = now()
				WHERE id = %s
				RETURNING id, email, display_name, status, xmpp_jid, xmpp_provisioning_status, xmpp_provisioning_error
				''',
				(user_id,)
			)
			updated_user = cursor.fetchone()
			write_xmpp_audit(cursor, actor_user_id, user_id, 'xmpp_account_disabled', {'jid': user['xmpp_jid']})

		connection.commit()

	return updated_user


def fetch_user(cursor, user_id: str) -> dict | None:
	'''
	Return a portal user for provisioning.

	:param cursor: Open database cursor
	:param user_id: Portal user ID
	'''

	cursor.execute(
		'''
		SELECT
			id,
			email,
			display_name,
			status,
			xmpp_jid,
			xmpp_provisioning_status,
			xmpp_provisioning_error
		FROM users
		WHERE id = %s
		''',
		(user_id,)
	)

	return cursor.fetchone()


def provision_user(user_id: str, actor_user_id: str, xmpp_password: str) -> dict:
	'''
	Provision an approved portal user into Prosody.

	:param user_id: Portal user ID
	:param actor_user_id: Acting admin user ID
	:param xmpp_password: Temporary XMPP password
	'''

	if not xmpp_password:
		raise XmppProvisioningInputError('xmpp password is required')

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, actor_user_id)
			user = fetch_user(cursor, user_id)

			if not user:
				raise XmppProvisioningInputError('user not found')

			if user['status'] == 'suspended':
				record_failure(cursor, actor_user_id, user, 'suspended users cannot be provisioned')
				connection.commit()
				raise XmppProvisioningInputError('suspended users cannot be provisioned')

			if user['status'] != 'approved':
				record_failure(cursor, actor_user_id, user, 'only approved users can be provisioned')
				connection.commit()
				raise XmppProvisioningInputError('only approved users can be provisioned')

			jid = build_jid(cursor, user)

			try:
				call_prosody('create', jid, xmpp_password)
			except XmppProvisioningRemoteError as error:
				record_failure(cursor, actor_user_id, user, str(error), jid)
				connection.commit()
				raise

			cursor.execute(
				'''
				UPDATE users
				SET
					xmpp_jid = %s,
					xmpp_provisioning_status = 'provisioned',
					xmpp_provisioning_error = NULL,
					xmpp_provisioned_at = now(),
					xmpp_disabled_at = NULL,
					updated_at = now()
				WHERE id = %s
				RETURNING id, email, display_name, status, xmpp_jid, xmpp_provisioning_status, xmpp_provisioning_error
				''',
				(jid, user_id)
			)
			updated_user = cursor.fetchone()
			write_xmpp_audit(cursor, actor_user_id, user_id, 'xmpp_account_created', {'jid': jid})

		connection.commit()

	return updated_user


def read_error(error: urllib.error.HTTPError) -> str:
	'''
	Return a safe error message from a failed HTTP response.

	:param error: HTTP error
	'''

	try:
		body = error.read().decode('utf-8')
		data = json.loads(body)
	except (OSError, json.JSONDecodeError):
		return f'prosody provisioning failed with HTTP {error.code}'

	return data.get('error') or f'prosody provisioning failed with HTTP {error.code}'


def record_failure(cursor, actor_user_id: str, user: dict, error: str, jid: str | None = None):
	'''
	Record an XMPP provisioning failure.

	:param cursor: Open database cursor
	:param actor_user_id: Acting admin user ID
	:param user: User record
	:param error: Failure message
	:param jid: Optional attempted XMPP JID
	'''

	cursor.execute(
		'''
		UPDATE users
		SET
			xmpp_provisioning_status = 'failed',
			xmpp_provisioning_error = %s,
			updated_at = now()
		WHERE id = %s
		''',
		(error, user['id'])
	)
	write_xmpp_audit(cursor, actor_user_id, str(user['id']), 'xmpp_provisioning_failure', {'error': error, 'jid': jid or user['xmpp_jid']})


def require_admin(cursor, actor_user_id: str):
	'''
	Require an approved admin actor for XMPP provisioning.

	:param cursor: Open database cursor
	:param actor_user_id: Acting user ID
	'''

	user = rooms.fetch_user(cursor, actor_user_id)

	if not user or user['status'] != 'approved':
		raise XmppProvisioningUnauthorizedError('admin user is required')

	if not rooms.has_any_scoped_role(cursor, actor_user_id, ADMIN_ROLES):
		raise XmppProvisioningUnauthorizedError('admin role is required')


def write_xmpp_audit(cursor, actor_user_id: str, target_user_id: str, action: str, metadata: dict):
	'''
	Write an XMPP provisioning audit event.

	:param cursor: Open database cursor
	:param actor_user_id: Acting admin user ID
	:param target_user_id: Target portal user ID
	:param action: Audit action
	:param metadata: Audit metadata
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
		VALUES (%s, %s, 'user', %s, %s, %s::jsonb)
		''',
		(actor_user_id, target_user_id, target_user_id, action, json.dumps(metadata))
	)
