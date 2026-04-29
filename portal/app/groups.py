# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/groups.py

import json

from portal.app import db, rooms


GROUP_TYPES = {'administrative', 'ministry', 'mission', 'monastery', 'parish', 'shared'}


class GroupError(Exception):
	'''Base exception for group workflow failures.'''


class GroupInputError(GroupError):
	'''Raised when group input is invalid.'''


class GroupUnauthorizedError(GroupError):
	'''Raised when an actor cannot manage groups.'''


def add_membership(group_id: str, user_id: str, actor_user_id: str, status: str = 'active') -> dict:
	'''
	Add or restore a user membership in a group.

	:param group_id: Group ID
	:param user_id: User ID
	:param actor_user_id: Acting admin user ID
	:param status: Membership status
	'''

	validate_membership_status(status)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, actor_user_id)
			group = fetch_group(cursor, group_id)
			user  = rooms.fetch_user(cursor, user_id)

			if not group:
				raise GroupInputError('group not found')

			if not user:
				raise GroupInputError('user not found')

			cursor.execute(
				'''
				INSERT INTO group_memberships (
					group_id,
					user_id,
					status
				)
				VALUES (%s, %s, %s)
				ON CONFLICT (group_id, user_id) DO UPDATE
				SET
					status = EXCLUDED.status,
					updated_at = now()
				RETURNING
					id,
					group_id,
					user_id,
					status,
					created_at,
					updated_at
				''',
				(group_id, user_id, status)
			)
			membership = cursor.fetchone()
			write_group_audit(
				cursor,
				actor_user_id,
				user_id,
				group,
				'group_membership_granted',
				{'membership_id': str(membership['id']), 'status': status}
			)

		connection.commit()

	return membership


def create_group(
	actor_user_id: str,
	name: str,
	slug: str,
	group_type: str,
	description: str | None = None,
	parent_group_id: str | None = None
) -> dict:
	'''
	Create a portal-managed group or parish.

	:param actor_user_id: Acting admin user ID
	:param name: Group name
	:param slug: Stable group slug
	:param group_type: Group type
	:param description: Optional group description
	:param parent_group_id: Optional parent group ID
	'''

	name        = clean_required(name, 'group name is required')
	slug        = clean_required(slug, 'group slug is required')
	description = clean_optional(description)
	validate_group_type(group_type)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, actor_user_id)
			validate_parent_group(cursor, parent_group_id)
			cursor.execute(
				'''
				INSERT INTO groups (
					parent_group_id,
					name,
					slug,
					group_type,
					description
				)
				VALUES (%s, %s, %s, %s, %s)
				RETURNING
					id,
					parent_group_id,
					name,
					slug,
					group_type,
					description,
					created_at,
					updated_at
				''',
				(parent_group_id, name, slug, group_type, description)
			)
			group = cursor.fetchone()
			write_group_audit(cursor, actor_user_id, None, group, 'group_created', {'group_type': group_type})

		connection.commit()

	return group


def clean_optional(value: str | None) -> str | None:
	'''
	Return stripped optional text.

	:param value: Raw value
	'''

	if value is None:
		return None

	cleaned = value.strip()

	return cleaned or None


def clean_required(value: str | None, error: str) -> str:
	'''
	Return stripped required text.

	:param value: Raw value
	:param error: Error text
	'''

	cleaned = clean_optional(value)

	if not cleaned:
		raise GroupInputError(error)

	return cleaned


def fetch_group(cursor, group_id: str) -> dict | None:
	'''
	Return a group record by ID.

	:param cursor: Open database cursor
	:param group_id: Group ID
	'''

	cursor.execute(
		'''
		SELECT
			id,
			parent_group_id,
			name,
			slug,
			group_type,
			description,
			created_at,
			updated_at
		FROM groups
		WHERE id = %s
		''',
		(group_id,)
	)

	return cursor.fetchone()


def list_groups() -> list[dict]:
	'''Return all groups and parishes.'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT
					id,
					parent_group_id,
					name,
					slug,
					group_type,
					description,
					created_at,
					updated_at
				FROM groups
				ORDER BY name ASC
				'''
			)

			return cursor.fetchall()


def list_memberships(group_id: str | None = None, user_id: str | None = None) -> list[dict]:
	'''
	Return group membership records.

	:param group_id: Optional group ID filter
	:param user_id: Optional user ID filter
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT
					gm.id,
					gm.group_id,
					g.name,
					g.slug,
					g.group_type,
					gm.user_id,
					u.email,
					u.display_name,
					gm.status,
					gm.created_at,
					gm.updated_at
				FROM group_memberships gm
				JOIN groups g ON g.id = gm.group_id
				JOIN users u ON u.id = gm.user_id
				WHERE (%s::uuid IS NULL OR gm.group_id = %s::uuid)
					AND (%s::uuid IS NULL OR gm.user_id = %s::uuid)
				ORDER BY g.name ASC, u.display_name ASC
				''',
				(group_id, group_id, user_id, user_id)
			)

			return cursor.fetchall()


def remove_membership(group_id: str, user_id: str, actor_user_id: str) -> dict:
	'''
	Mark a group membership removed.

	:param group_id: Group ID
	:param user_id: User ID
	:param actor_user_id: Acting admin user ID
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, actor_user_id)
			group = fetch_group(cursor, group_id)

			if not group:
				raise GroupInputError('group not found')

			cursor.execute(
				'''
				UPDATE group_memberships
				SET
					status = 'removed',
					updated_at = now()
				WHERE group_id = %s
					AND user_id = %s
					AND status != 'removed'
				RETURNING
					id,
					group_id,
					user_id,
					status,
					created_at,
					updated_at
				''',
				(group_id, user_id)
			)
			membership = cursor.fetchone()

			if not membership:
				raise GroupInputError('active group membership not found')

			write_group_audit(
				cursor,
				actor_user_id,
				user_id,
				group,
				'group_membership_removed',
				{'membership_id': str(membership['id'])}
			)

		connection.commit()

	return membership


def require_admin(cursor, actor_user_id: str):
	'''
	Require an approved admin actor for group management.

	:param cursor: Open database cursor
	:param actor_user_id: Acting user ID
	'''

	user = rooms.fetch_user(cursor, actor_user_id)

	if not user or user['status'] != 'approved':
		raise GroupUnauthorizedError('admin user is required')

	if not rooms.has_any_scoped_role(cursor, actor_user_id, rooms.ADMIN_ROLES):
		raise GroupUnauthorizedError('admin role is required')


def update_group(
	actor_user_id: str,
	group_id: str,
	name: str,
	slug: str,
	group_type: str,
	description: str | None = None,
	parent_group_id: str | None = None
) -> dict:
	'''
	Update group or parish metadata.

	:param actor_user_id: Acting admin user ID
	:param group_id: Group ID
	:param name: Group name
	:param slug: Stable group slug
	:param group_type: Group type
	:param description: Optional description
	:param parent_group_id: Optional parent group ID
	'''

	name        = clean_required(name, 'group name is required')
	slug        = clean_required(slug, 'group slug is required')
	description = clean_optional(description)
	validate_group_type(group_type)

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			require_admin(cursor, actor_user_id)
			current_group = fetch_group(cursor, group_id)

			if not current_group:
				raise GroupInputError('group not found')

			if parent_group_id == group_id:
				raise GroupInputError('group cannot be its own parent')

			validate_parent_group(cursor, parent_group_id)
			cursor.execute(
				'''
				UPDATE groups
				SET
					parent_group_id = %s,
					name = %s,
					slug = %s,
					group_type = %s,
					description = %s,
					updated_at = now()
				WHERE id = %s
				RETURNING
					id,
					parent_group_id,
					name,
					slug,
					group_type,
					description,
					created_at,
					updated_at
				''',
				(parent_group_id, name, slug, group_type, description, group_id)
			)
			group = cursor.fetchone()
			write_group_audit(
				cursor,
				actor_user_id,
				None,
				group,
				'group_updated',
				{
					'old_name': current_group['name'],
					'old_slug': current_group['slug'],
					'old_group_type': current_group['group_type']
				}
			)

		connection.commit()

	return group


def validate_group_type(group_type: str):
	'''
	Validate a supported group type.

	:param group_type: Group type
	'''

	if group_type not in GROUP_TYPES:
		raise GroupInputError('unsupported group type')


def validate_membership_status(status: str):
	'''
	Validate group membership status.

	:param status: Membership status
	'''

	if status not in {'active', 'invited', 'pending', 'suspended'}:
		raise GroupInputError('unsupported membership status')


def validate_parent_group(cursor, parent_group_id: str | None):
	'''
	Validate an optional parent group.

	:param cursor: Open database cursor
	:param parent_group_id: Optional parent group ID
	'''

	if not parent_group_id:
		return

	if not fetch_group(cursor, parent_group_id):
		raise GroupInputError('parent group not found')


def write_group_audit(cursor, actor_user_id: str, target_user_id: str | None, group: dict, action: str, metadata: dict):
	'''
	Write a group-related audit event.

	:param cursor: Open database cursor
	:param actor_user_id: Acting user ID
	:param target_user_id: Optional target user ID
	:param group: Group record
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
		VALUES (%s, %s, 'group', %s, %s, %s, %s::jsonb)
		''',
		(
			actor_user_id,
			target_user_id,
			group['id'],
			action,
			group['id'],
			json.dumps(metadata)
		)
	)
