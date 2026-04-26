# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/meetings.py

import base64
import hashlib
import hmac
import json
import secrets

from datetime import datetime, timedelta, timezone

from portal.app import config, db, rooms


class MeetingAccessError(Exception):
	'''Base exception for meeting access workflow failures.'''


class MeetingDeniedError(MeetingAccessError):
	'''Raised when meeting access is denied.'''


class MeetingInputError(MeetingAccessError):
	'''Raised when meeting input is invalid.'''


def base64url(data: bytes) -> str:
	'''
	Return base64url text without padding.

	:param data: Raw bytes
	'''

	return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')


def can_create_meeting(cursor, user_id: str, room_id: str | None = None) -> bool:
	'''
	Return whether a user may create an official meeting.

	:param cursor: Open database cursor
	:param user_id: User ID
	:param room_id: Optional portal room ID
	'''

	user = rooms.fetch_user(cursor, user_id)

	if not user or user['status'] != 'approved':
		return False

	room = None

	if room_id:
		room = rooms.fetch_room(cursor, room_id)

		if not room:
			raise MeetingInputError('room not found')

		if not rooms.can_access_room_record(cursor, room, user_id):
			return False

	group_id = room['group_id'] if room else None

	return rooms.has_any_scoped_role(cursor, user_id, config.jitsi_meeting_creator_roles(), group_id)


def create_guest(meeting_id: str, actor_user_id: str, display_name: str, expires_at: datetime, email: str | None = None) -> dict:
	'''
	Create an explicitly allowed meeting guest.

	:param meeting_id: Meeting ID
	:param actor_user_id: User ID creating the guest
	:param display_name: Guest display name
	:param expires_at: Guest access expiration
	:param email: Optional guest email
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			meeting = fetch_meeting(cursor, meeting_id)

			if not meeting:
				raise MeetingInputError('meeting not found')

			if not meeting['allow_guests']:
				raise MeetingDeniedError('meeting does not allow guests')

			if not can_create_meeting(cursor, actor_user_id, meeting['room_id']):
				raise MeetingDeniedError('actor cannot manage this meeting')

			cursor.execute(
				'''
				INSERT INTO meeting_guests (
					meeting_id,
					display_name,
					email,
					expires_at,
					created_by_user_id
				)
				VALUES (%s, %s, %s, %s, %s)
				RETURNING
					id,
					meeting_id,
					display_name,
					email,
					status,
					expires_at,
					created_by_user_id,
					created_at,
					updated_at
				''',
				(meeting_id, display_name, email, expires_at, actor_user_id)
			)
			guest = cursor.fetchone()

			write_meeting_audit(
				cursor,
				actor_user_id,
				None,
				meeting,
				'meeting_guest_allowed',
				{'guest_id': str(guest['id']), 'expires_at': expires_at.isoformat()}
			)

		connection.commit()

	return guest


def create_meeting(actor_user_id: str, name: str, slug: str, room_id: str | None = None, allow_guests: bool = False) -> dict:
	'''
	Create an official Jitsi meeting room.

	:param actor_user_id: User ID creating the meeting
	:param name: Meeting display name
	:param slug: Stable meeting slug
	:param room_id: Optional portal room ID used for access policy
	:param allow_guests: Whether explicit guests may join
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			if not can_create_meeting(cursor, actor_user_id, room_id):
				raise MeetingDeniedError('user cannot create official meetings')

			jitsi_room_name = normalize_jitsi_room_name(slug)
			cursor.execute(
				'''
				INSERT INTO meetings (
					room_id,
					created_by_user_id,
					name,
					slug,
					jitsi_room_name,
					allow_guests
				)
				VALUES (%s, %s, %s, %s, %s, %s)
				RETURNING
					id,
					room_id,
					created_by_user_id,
					name,
					slug,
					jitsi_room_name,
					allow_guests,
					status,
					created_at,
					updated_at
				''',
				(room_id, actor_user_id, name, slug, jitsi_room_name, allow_guests)
			)
			meeting = cursor.fetchone()

			write_meeting_audit(
				cursor,
				actor_user_id,
				None,
				meeting,
				'meeting_created',
				{'allow_guests': allow_guests, 'room_id': str(room_id) if room_id else None}
			)

		connection.commit()

	return meeting


def encode_jwt(payload: dict) -> str:
	'''
	Return a signed HS256 JWT.

	:param payload: JWT payload
	'''

	header         = {'alg': 'HS256', 'typ': 'JWT'}
	signing_input = f'{base64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))}.{base64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))}'
	signature     = hmac.new(config.jitsi_jwt_app_secret().encode('utf-8'), signing_input.encode('ascii'), hashlib.sha256).digest()

	return f'{signing_input}.{base64url(signature)}'


def fetch_guest(cursor, guest_id: str) -> dict | None:
	'''
	Return a meeting guest record by ID.

	:param cursor: Open database cursor
	:param guest_id: Guest ID
	'''

	cursor.execute(
		'''
		SELECT
			id,
			meeting_id,
			display_name,
			email,
			status,
			expires_at,
			created_by_user_id,
			created_at,
			updated_at
		FROM meeting_guests
		WHERE id = %s
		''',
		(guest_id,)
	)

	return cursor.fetchone()


def fetch_meeting(cursor, meeting_id: str) -> dict | None:
	'''
	Return a meeting record by ID.

	:param cursor: Open database cursor
	:param meeting_id: Meeting ID
	'''

	cursor.execute(
		'''
		SELECT
			id,
			room_id,
			created_by_user_id,
			name,
			slug,
			jitsi_room_name,
			allow_guests,
			status,
			created_at,
			updated_at
		FROM meetings
		WHERE id = %s
		''',
		(meeting_id,)
	)

	return cursor.fetchone()


def issue_guest_token(meeting_id: str, guest_id: str, issued_by_user_id: str, ttl_seconds: int | None = None) -> dict:
	'''
	Issue a Jitsi JWT for an explicitly allowed guest.

	:param meeting_id: Meeting ID
	:param guest_id: Guest ID
	:param issued_by_user_id: User ID issuing the token
	:param ttl_seconds: Optional token lifetime in seconds
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			meeting = fetch_meeting(cursor, meeting_id)
			guest   = fetch_guest(cursor, guest_id)

			if not meeting:
				raise MeetingInputError('meeting not found')

			if not guest or guest['meeting_id'] != meeting['id']:
				raise MeetingInputError('guest not found for meeting')

			if not can_create_meeting(cursor, issued_by_user_id, meeting['room_id']):
				raise MeetingDeniedError('actor cannot issue guest tokens for this meeting')

			if meeting['status'] != 'active' or not meeting['allow_guests']:
				raise MeetingDeniedError('meeting does not allow guest access')

			if guest['status'] != 'active' or guest['expires_at'] <= datetime.now(timezone.utc):
				raise MeetingDeniedError('guest access is not active')

			token_ttl  = ttl_seconds or config.jitsi_token_ttl_seconds()
			expires_at = min(datetime.now(timezone.utc) + timedelta(seconds=token_ttl), guest['expires_at'])
			result     = issue_token_record(cursor, meeting, issued_by_user_id, None, guest, expires_at)

		connection.commit()

	return result


def issue_token_record(cursor, meeting: dict, issued_by_user_id: str, user: dict | None, guest: dict | None, expires_at: datetime) -> dict:
	'''
	Create token issuance state, audit it, and return link details.

	:param cursor: Open database cursor
	:param meeting: Meeting record
	:param issued_by_user_id: User ID issuing the token
	:param user: Optional portal user record
	:param guest: Optional meeting guest record
	:param expires_at: Token expiration timestamp
	'''

	now      = datetime.now(timezone.utc)
	token_id = secrets.token_urlsafe(18)
	context  = {
		'user': {
			'id': str(user['id']) if user else str(guest['id']),
			'name': user['display_name'] if user else guest['display_name']
		}
	}

	if user and user['email']:
		context['user']['email'] = user['email']

	if guest and guest['email']:
		context['user']['email'] = guest['email']

	payload = {
		'aud': config.jitsi_jwt_app_id(),
		'context': context,
		'exp': int(expires_at.timestamp()),
		'iat': int(now.timestamp()),
		'iss': config.jitsi_jwt_app_id(),
		'nbf': int(now.timestamp()),
		'room': meeting['jitsi_room_name'],
		'sub': config.jitsi_xmpp_domain()
	}
	token = encode_jwt(payload)

	cursor.execute(
		'''
		INSERT INTO meeting_token_issuances (
			meeting_id,
			user_id,
			guest_id,
			issued_by_user_id,
			token_id,
			expires_at,
			created_at
		)
		VALUES (%s, %s, %s, %s, %s, %s, %s)
		RETURNING
			id,
			meeting_id,
			user_id,
			guest_id,
			issued_by_user_id,
			token_id,
			expires_at,
			created_at
		''',
		(
			meeting['id'],
			user['id'] if user else None,
			guest['id'] if guest else None,
			issued_by_user_id,
			token_id,
			expires_at,
			now
		)
	)
	issuance = cursor.fetchone()

	write_meeting_audit(
		cursor,
		issued_by_user_id,
		user['id'] if user else None,
		meeting,
		'meeting_token_issued',
		{
			'guest_id': str(guest['id']) if guest else None,
			'token_id': token_id,
			'expires_at': expires_at.isoformat()
		}
	)

	return {
		'expires_at': expires_at,
		'join_url': f'{config.jitsi_public_url()}/{meeting["jitsi_room_name"]}?jwt={token}',
		'meeting_id': meeting['id'],
		'token': token,
		'token_id': issuance['token_id']
	}


def issue_user_token(meeting_id: str, user_id: str, issued_by_user_id: str | None = None, ttl_seconds: int | None = None) -> dict:
	'''
	Issue a Jitsi JWT for an approved portal user allowed by meeting policy.

	:param meeting_id: Meeting ID
	:param user_id: User ID receiving the token
	:param issued_by_user_id: User ID issuing the token
	:param ttl_seconds: Optional token lifetime in seconds
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			meeting = fetch_meeting(cursor, meeting_id)

			if not meeting:
				raise MeetingInputError('meeting not found')

			user = fetch_user_profile(cursor, user_id)

			if not user or user['status'] != 'approved':
				raise MeetingDeniedError('user is not approved')

			if meeting['status'] != 'active':
				raise MeetingDeniedError('meeting is not active')

			if meeting['room_id']:
				room = rooms.fetch_room(cursor, meeting['room_id'])

				if not room or not rooms.can_access_room_record(cursor, room, user_id):
					raise MeetingDeniedError('user cannot access this meeting room')

			actor_id = issued_by_user_id or user_id

			if actor_id != user_id and not can_create_meeting(cursor, actor_id, meeting['room_id']):
				raise MeetingDeniedError('actor cannot issue user tokens for this meeting')

			token_ttl  = ttl_seconds or config.jitsi_token_ttl_seconds()
			expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_ttl)
			result     = issue_token_record(cursor, meeting, actor_id, user, None, expires_at)

		connection.commit()

	return result


def fetch_user_profile(cursor, user_id: str) -> dict | None:
	'''
	Return user profile fields needed for Jitsi tokens.

	:param cursor: Open database cursor
	:param user_id: User ID
	'''

	cursor.execute(
		'''
		SELECT
			id,
			display_name,
			email,
			status
		FROM users
		WHERE id = %s
		''',
		(user_id,)
	)

	return cursor.fetchone()


def list_meetings() -> list[dict]:
	'''
	Return all Jitsi meetings.
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute(
				'''
				SELECT
					id,
					room_id,
					created_by_user_id,
					name,
					slug,
					jitsi_room_name,
					allow_guests,
					status,
					created_at,
					updated_at
				FROM meetings
				ORDER BY created_at DESC
				'''
			)

			return cursor.fetchall()


def normalize_jitsi_room_name(slug: str) -> str:
	'''
	Return a Jitsi-safe room name.

	:param slug: Meeting slug
	'''

	cleaned = ''.join(character for character in slug.lower() if character.isalnum() or character in '-_')

	if not cleaned:
		raise MeetingInputError('meeting slug must contain letters or numbers')

	return cleaned


def parse_expiration(value: str | None, ttl_seconds: int | None = None) -> datetime:
	'''
	Return an expiration timestamp from an ISO value or TTL.

	:param value: Optional ISO timestamp
	:param ttl_seconds: Optional TTL seconds
	'''

	if value:
		parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))

		if parsed.tzinfo:
			return parsed

		return parsed.replace(tzinfo=timezone.utc)

	return datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds or config.jitsi_token_ttl_seconds())


def write_meeting_audit(cursor, actor_user_id: str, target_user_id: str | None, meeting: dict, action: str, metadata: dict):
	'''
	Write a meeting-related audit event.

	:param cursor: Open database cursor
	:param actor_user_id: Acting user ID
	:param target_user_id: Optional target user ID
	:param meeting: Meeting record
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
		VALUES (%s, %s, 'meeting', %s, %s, %s::jsonb)
		''',
		(
			actor_user_id,
			target_user_id,
			meeting['id'],
			action,
			json.dumps(metadata)
		)
	)
