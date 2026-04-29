# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/rooms.py

import json
import re
import urllib.error
import urllib.request

from portal.app import config, db


ADMIN_ROLES  = {'diocesan_admin', 'parish_admin', 'platform_admin'}
RESERVED_ROOM_NODES = {'admin', 'administrator', 'clergy', 'conference', 'monastic', 'prosody', 'root', 'support'}
ROOM_SCOPES  = {'admin_only', 'clergy_only', 'group_only', 'invite_only', 'monastic_only', 'public_to_members'}
ROOM_ROLES   = {'admin', 'member', 'moderator'}
USER_ALLOWED = {'approved'}


class RoomAccessError(Exception):
	'''Base exception for room access workflow failures.'''


class RoomDeniedError(RoomAccessError):
	'''Raised when room access is denied.'''


class RoomInputError(RoomAccessError):
	'''Raised when room input is invalid.'''


class RoomProvisioningError(RoomAccessError):
	'''Raised when MUC room provisioning fails.'''


def add_room_membership(room_id: str, user_id: str, actor_user_id: str, role: str = 'member') -> dict:
	'''
	Add an explicit room membership when room rules allow it.

	:param room_id: Room ID
	:param user_id: User ID
	:param actor_user_id: User ID making the membership change
	:param role: Room membership role
	'''

	if role not in ROOM_ROLES:
		raise RoomInputError('unsupported room membership role')

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			room = fetch_room(cursor, room_id)

			if not room:
				raise RoomInputError('room not found')

			if not can_create_membership(cursor, room, user_id):
				raise RoomDeniedError('room rules do not allow this membership')

			cursor.execute(
				'''
				INSERT INTO room_memberships (
					room_id,
					user_id,
					role,
					status
				)
				VALUES (%s, %s, %s, 'active')
				ON CONFLICT (room_id, user_id) DO UPDATE
				SET
					role = EXCLUDED.role,
					status = 'active',
					updated_at = now()
				RETURNING
					id,
					room_id,
					user_id,
					role,
					status,
					created_at,
					updated_at
				''',
				(room_id, user_id, role)
			)
			membership = cursor.fetchone()

			write_room_audit(
				cursor,
				actor_user_id,
				user_id,
				room,
				'room_membership_added',
				{'membership_id': str(membership['id']), 'role': role}
			)

		connection.commit()

	return membership


def can_access_room(room_id: str, user_id: str) -> bool:
	'''
	Return whether a user can access a room.

	:param room_id: Room ID
	:param user_id: User ID
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			room = fetch_room(cursor, room_id)

			if not room:
				raise RoomInputError('room not found')

			return can_access_room_record(cursor, room, user_id)


def can_access_room_record(cursor, room: dict, user_id: str) -> bool:
	'''
	Return whether a user can access a fetched room record.

	:param cursor: Open database cursor
	:param room: Room record
	:param user_id: User ID
	'''

	user = fetch_user(cursor, user_id)

	if not user or user['status'] not in USER_ALLOWED:
		return False

	if has_active_room_membership(cursor, room['id'], user_id):
		return True

	scope = room['privacy_level']

	if scope == 'invite_only':
		return False

	if scope == 'public_to_members':
		return has_any_active_group_membership(cursor, user_id)

	if scope == 'group_only':
		return bool(room['group_id']) and has_required_group_context(cursor, user_id, room['group_id'])

	if scope == 'clergy_only':
		return has_scoped_role(cursor, user_id, 'clergy_verified', room['group_id']) and has_required_group_context(cursor, user_id, room['group_id'])

	if scope == 'monastic_only':
		return has_scoped_role(cursor, user_id, 'monastic_verified', room['group_id']) and has_required_group_context(cursor, user_id, room['group_id'])

	if scope == 'admin_only':
		return has_any_scoped_role(cursor, user_id, ADMIN_ROLES, room['group_id']) and has_required_group_context(cursor, user_id, room['group_id'])

	return False


def can_create_membership(cursor, room: dict, user_id: str) -> bool:
	'''
	Return whether an explicit room membership can be created.

	:param cursor: Open database cursor
	:param room: Room record
	:param user_id: User ID
	'''

	user = fetch_user(cursor, user_id)

	if not user or user['status'] not in USER_ALLOWED:
		return False

	if room['privacy_level'] == 'invite_only':
		return True

	return can_access_room_record(cursor, room, user_id)


def create_room(
	actor_user_id: str,
	name: str,
	slug: str,
	privacy_level: str,
	group_id: str | None = None,
	xmpp_room_jid: str | None = None
) -> dict:
	'''
	Create a room/channel with an access scope and record an audit event.

	:param actor_user_id: User ID creating the room
	:param name: Room display name
	:param slug: Stable room slug
	:param privacy_level: Room access scope
	:param group_id: Optional group scope
	:param xmpp_room_jid: Optional Prosody room JID
	'''

	validate_room_scope(privacy_level)
	validate_room_group_scope(privacy_level, group_id)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			if not fetch_user(cursor, actor_user_id):
				raise RoomInputError('actor user not found')

			cursor.execute(
				'''
				INSERT INTO rooms (
					created_by_user_id,
					group_id,
					name,
					slug,
					xmpp_room_jid,
					privacy_level
				)
				VALUES (%s, %s, %s, %s, %s, %s)
				RETURNING
					id,
					created_by_user_id,
					group_id,
					name,
					slug,
					xmpp_room_jid,
					muc_provisioning_status,
					muc_provisioning_error,
					privacy_level,
					created_at,
					updated_at
				''',
				(actor_user_id, group_id, name, slug, xmpp_room_jid, privacy_level)
			)
			room = cursor.fetchone()

			write_room_audit(
				cursor,
				actor_user_id,
				None,
				room,
				'room_created',
				{'privacy_level': privacy_level}
			)

		connection.commit()

	return room


def change_room_access(actor_user_id: str, room_id: str, privacy_level: str, group_id: str | None = None) -> dict:
	'''
	Change a room access scope and record an audit event.

	:param actor_user_id: User ID changing the room access
	:param room_id: Room ID
	:param privacy_level: New room access scope
	:param group_id: Optional group scope
	'''

	validate_room_scope(privacy_level)
	validate_room_group_scope(privacy_level, group_id)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			room = fetch_room(cursor, room_id)

			if not room:
				raise RoomInputError('room not found')

			if not fetch_user(cursor, actor_user_id):
				raise RoomInputError('actor user not found')

			cursor.execute(
				'''
				UPDATE rooms
				SET
					group_id = %s,
					privacy_level = %s,
					updated_at = now()
				WHERE id = %s
				RETURNING
					id,
					created_by_user_id,
					group_id,
					name,
					slug,
					xmpp_room_jid,
					privacy_level,
					created_at,
					updated_at
				''',
				(group_id, privacy_level, room_id)
			)
			updated_room = cursor.fetchone()

			write_room_audit(
				cursor,
				actor_user_id,
				None,
				updated_room,
				'room_access_changed',
				{
					'old_group_id': str(room['group_id']) if room['group_id'] else None,
					'old_privacy_level': room['privacy_level'],
					'new_group_id': str(group_id) if group_id else None,
					'new_privacy_level': privacy_level
				}
			)

		connection.commit()

	return updated_room


def build_muc_room_jid(cursor, room: dict) -> str:
	'''
	Build a safe MUC JID for a portal room.

	:param cursor: Open database cursor
	:param room: Room record
	'''

	if room['xmpp_room_jid']:
		return room['xmpp_room_jid']

	node = re.sub(r'[^a-z0-9_.-]+', '-', (room['slug'] or room['name']).lower()).strip('._-')

	if not node or len(node) < 3 or node in RESERVED_ROOM_NODES:
		node = f'room-{str(room["id"])[:8]}'

	node     = node[:48].strip('._-') or f'room-{str(room["id"])[:8]}'
	room_jid = f'{node}@{config.xmpp_muc_domain()}'

	cursor.execute('SELECT id FROM rooms WHERE xmpp_room_jid = %s AND id != %s', (room_jid, room['id']))

	if cursor.fetchone():
		room_jid = f'{node}-{str(room["id"])[:8]}@{config.xmpp_muc_domain()}'

	return room_jid


def call_prosody_room(payload: dict) -> dict:
	'''
	Send a MUC provisioning request to Prosody.

	:param payload: Provisioning payload
	'''

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
		raise RoomProvisioningError(read_prosody_error(error)) from error
	except (OSError, json.JSONDecodeError) as error:
		raise RoomProvisioningError(str(error)) from error


def eligible_room_member_jids(cursor, room: dict) -> list[str]:
	'''
	Return provisioned XMPP JIDs allowed to access a room.

	:param cursor: Open database cursor
	:param room: Room record
	'''

	cursor.execute(
		'''
		SELECT id, xmpp_jid
		FROM users
		WHERE status = 'approved'
			AND xmpp_jid IS NOT NULL
			AND xmpp_provisioning_status = 'provisioned'
		ORDER BY xmpp_jid ASC
		'''
	)

	return [user['xmpp_jid'] for user in cursor.fetchall() if can_access_room_record(cursor, room, str(user['id']))]


def accessible_rooms_for_user(user_id: str) -> list[dict]:
	'''
	Return rooms visible to the given portal user.

	:param user_id: Portal user ID
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT
					id,
					created_by_user_id,
					group_id,
					name,
					slug,
					xmpp_room_jid,
					muc_provisioning_status,
					muc_provisioning_error,
					privacy_level,
					created_at,
					updated_at
				FROM rooms
				ORDER BY name ASC
				'''
			)

			return [room for room in cursor.fetchall() if can_access_room_record(cursor, room, user_id)]


def fetch_room(cursor, room_id: str) -> dict | None:
	'''
	Return a room record by ID.

	:param cursor: Open database cursor
	:param room_id: Room ID
	'''

	cursor.execute(
		'''
		SELECT
			id,
			created_by_user_id,
			group_id,
			name,
			slug,
			xmpp_room_jid,
			muc_provisioning_status,
			muc_provisioning_error,
			privacy_level,
			created_at,
			updated_at
		FROM rooms
		WHERE id = %s
		''',
		(room_id,)
	)

	return cursor.fetchone()


def open_room(room_id: str, user_id: str) -> dict:
	'''
	Record that a user opened a permitted room and return the room.

	:param room_id: Portal room ID
	:param user_id: Portal user ID
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			room = fetch_room(cursor, room_id)

			if not room:
				raise RoomInputError('room not found')

			if not can_access_room_record(cursor, room, user_id):
				raise RoomDeniedError('room access denied')

			write_room_audit(
				cursor,
				user_id,
				user_id,
				room,
				'room_opened',
				{'xmpp_room_jid': room['xmpp_room_jid'], 'muc_provisioning_status': room['muc_provisioning_status']}
			)

		connection.commit()

	return room


def provision_muc_room(room_id: str, actor_user_id: str) -> dict:
	'''
	Provision a portal room into Prosody MUC.

	:param room_id: Portal room ID
	:param actor_user_id: Acting admin user ID
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, actor_user_id)
			room = fetch_room(cursor, room_id)

			if not room:
				raise RoomInputError('room not found')

			room_jid = build_muc_room_jid(cursor, room)
			payload  = {
				'action': 'create_room',
				'description': f'Orthodox Connect {room["privacy_level"]} room',
				'members': eligible_room_member_jids(cursor, room),
				'members_only': True,
				'moderated': room['privacy_level'] == 'admin_only',
				'name': room['name'],
				'privacy_level': room['privacy_level'],
				'public': False,
				'room_jid': room_jid,
			}

			try:
				result = call_prosody_room(payload)
			except RoomProvisioningError as error:
				record_muc_failure(cursor, actor_user_id, room, str(error), room_jid)
				connection.commit()
				raise

			cursor.execute(
				'''
				UPDATE rooms
				SET
					xmpp_room_jid = %s,
					muc_provisioning_status = 'provisioned',
					muc_provisioning_error = NULL,
					muc_provisioned_at = now(),
					updated_at = now()
				WHERE id = %s
				RETURNING
					id,
					created_by_user_id,
					group_id,
					name,
					slug,
					xmpp_room_jid,
					muc_provisioning_status,
					muc_provisioning_error,
					privacy_level,
					created_at,
					updated_at
				''',
				(room_jid, room_id)
			)
			updated_room = cursor.fetchone()
			action       = 'muc_room_created' if result.get('status') == 'created' else 'muc_room_updated'
			write_room_audit(cursor, actor_user_id, None, updated_room, action, {'xmpp_room_jid': room_jid, 'members': len(payload['members'])})

		connection.commit()

	return updated_room


def read_prosody_error(error: urllib.error.HTTPError) -> str:
	'''
	Return a safe error message from a failed Prosody response.

	:param error: HTTP error
	'''

	try:
		body = error.read().decode('utf-8')
		data = json.loads(body)
	except (OSError, json.JSONDecodeError):
		return f'prosody muc provisioning failed with HTTP {error.code}'

	return data.get('error') or f'prosody muc provisioning failed with HTTP {error.code}'


def record_muc_failure(cursor, actor_user_id: str, room: dict, error: str, room_jid: str):
	'''
	Record a MUC provisioning failure.

	:param cursor: Open database cursor
	:param actor_user_id: Acting admin user ID
	:param room: Room record
	:param error: Failure message
	:param room_jid: Attempted MUC room JID
	'''

	cursor.execute(
		'''
		UPDATE rooms
		SET
			muc_provisioning_status = 'failed',
			muc_provisioning_error = %s,
			updated_at = now()
		WHERE id = %s
		''',
		(error, room['id'])
	)
	write_room_audit(cursor, actor_user_id, None, room, 'muc_provisioning_failure', {'error': error, 'xmpp_room_jid': room_jid})


def require_admin(cursor, actor_user_id: str):
	'''
	Require an approved admin actor for room provisioning.

	:param cursor: Open database cursor
	:param actor_user_id: Acting user ID
	'''

	user = fetch_user(cursor, actor_user_id)

	if not user or user['status'] != 'approved':
		raise RoomDeniedError('admin user is required')

	if not has_any_scoped_role(cursor, actor_user_id, ADMIN_ROLES):
		raise RoomDeniedError('admin role is required')


def fetch_user(cursor, user_id: str) -> dict | None:
	'''
	Return a user record by ID.

	:param cursor: Open database cursor
	:param user_id: User ID
	'''

	cursor.execute('SELECT id, status FROM users WHERE id = %s', (user_id,))

	return cursor.fetchone()


def has_active_group_membership(cursor, user_id: str, group_id: str) -> bool:
	'''
	Return whether a user has active membership in a group.

	:param cursor: Open database cursor
	:param user_id: User ID
	:param group_id: Group ID
	'''

	cursor.execute(
		'''
		SELECT 1
		FROM group_memberships
		WHERE user_id = %s
			AND group_id = %s
			AND status = 'active'
		''',
		(user_id, group_id)
	)

	return cursor.fetchone() is not None


def has_active_room_membership(cursor, room_id: str, user_id: str) -> bool:
	'''
	Return whether a user has active explicit membership in a room.

	:param cursor: Open database cursor
	:param room_id: Room ID
	:param user_id: User ID
	'''

	cursor.execute(
		'''
		SELECT 1
		FROM room_memberships
		WHERE room_id = %s
			AND user_id = %s
			AND status = 'active'
		''',
		(room_id, user_id)
	)

	return cursor.fetchone() is not None


def has_any_active_group_membership(cursor, user_id: str) -> bool:
	'''
	Return whether a user has any active group membership.

	:param cursor: Open database cursor
	:param user_id: User ID
	'''

	cursor.execute(
		'''
		SELECT 1
		FROM group_memberships
		WHERE user_id = %s
			AND status = 'active'
		LIMIT 1
		''',
		(user_id,)
	)

	return cursor.fetchone() is not None


def has_any_scoped_role(cursor, user_id: str, role_names: set[str], group_id: str | None = None) -> bool:
	'''
	Return whether a user has any scoped role.

	:param cursor: Open database cursor
	:param user_id: User ID
	:param role_names: Role names
	:param group_id: Optional group scope
	'''

	for role_name in role_names:
		if has_scoped_role(cursor, user_id, role_name, group_id):
			return True

	return False


def has_required_group_context(cursor, user_id: str, group_id: str | None) -> bool:
	'''
	Return whether room group context allows the user.

	:param cursor: Open database cursor
	:param user_id: User ID
	:param group_id: Optional group scope
	'''

	if not group_id:
		return has_any_active_group_membership(cursor, user_id)

	return has_active_group_membership(cursor, user_id, group_id)


def has_scoped_role(cursor, user_id: str, role_name: str, group_id: str | None = None) -> bool:
	'''
	Return whether a user has a role globally or in the room group.

	:param cursor: Open database cursor
	:param user_id: User ID
	:param role_name: Role name
	:param group_id: Optional group scope
	'''

	cursor.execute(
		'''
		SELECT 1
		FROM user_roles ur
		JOIN roles r ON r.id = ur.role_id
		WHERE ur.user_id = %s
			AND r.name = %s
			AND ur.revoked_at IS NULL
			AND (
				ur.group_id IS NULL
				OR %s::uuid IS NULL
				OR ur.group_id = %s::uuid
			)
		LIMIT 1
		''',
		(user_id, role_name, group_id, group_id)
	)

	return cursor.fetchone() is not None


def list_rooms() -> list[dict]:
	'''
	Return all rooms with their access scopes.
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT
					id,
					created_by_user_id,
					group_id,
					name,
					slug,
					xmpp_room_jid,
					privacy_level,
					created_at,
					updated_at
				FROM rooms
				ORDER BY created_at DESC
				'''
			)

			return cursor.fetchall()


def remove_room_membership(room_id: str, user_id: str, actor_user_id: str) -> dict:
	'''
	Mark a room membership removed and record an audit event.

	:param room_id: Room ID
	:param user_id: User ID
	:param actor_user_id: User ID making the membership change
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			room = fetch_room(cursor, room_id)

			if not room:
				raise RoomInputError('room not found')

			cursor.execute(
				'''
				UPDATE room_memberships
				SET
					status = 'removed',
					updated_at = now()
				WHERE room_id = %s
					AND user_id = %s
					AND status = 'active'
				RETURNING
					id,
					room_id,
					user_id,
					role,
					status,
					created_at,
					updated_at
				''',
				(room_id, user_id)
			)
			membership = cursor.fetchone()

			if not membership:
				raise RoomInputError('active room membership not found')

			write_room_audit(
				cursor,
				actor_user_id,
				user_id,
				room,
				'room_membership_removed',
				{'membership_id': str(membership['id'])}
			)

		connection.commit()

	return membership


def validate_room_scope(privacy_level: str):
	'''
	Validate a room access scope.

	:param privacy_level: Room access scope
	'''

	if privacy_level not in ROOM_SCOPES:
		raise RoomInputError('unsupported room access scope')


def validate_room_group_scope(privacy_level: str, group_id: str | None):
	'''
	Validate room scope and group pairing.

	:param privacy_level: Room access scope
	:param group_id: Optional group scope
	'''

	if privacy_level == 'group_only' and not group_id:
		raise RoomInputError('group_only rooms require a group_id')


def write_room_audit(cursor, actor_user_id: str, target_user_id: str | None, room: dict, action: str, metadata: dict):
	'''
	Write a room-related audit event.

	:param cursor: Open database cursor
	:param actor_user_id: Acting user ID
	:param target_user_id: Optional target user ID
	:param room: Room record
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
			scope_group_id,
			metadata
		)
		VALUES (%s, %s, 'room', %s, %s, %s, %s::jsonb)
		''',
		(
			actor_user_id,
			target_user_id,
			room['id'],
			action,
			room['group_id'],
			json.dumps(metadata)
		)
	)
