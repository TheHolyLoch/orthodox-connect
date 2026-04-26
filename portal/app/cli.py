#!/usr/bin/env python3
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/cli.py

import argparse
import json
import sys

from datetime import datetime, timedelta, timezone

from portal.app import invites, migrations, rooms, verifications


def add_create_invite_parser(subparsers):
	'''
	Add the create-invite subcommand parser.
	'''

	parser = subparsers.add_parser('create-invite')
	parser.add_argument('--created-by-user-id', required=True)
	parser.add_argument('--expected-role-id')
	parser.add_argument('--expires-at')
	parser.add_argument('--group-id')
	parser.add_argument('--reusable', action='store_true')
	parser.add_argument('--ttl-hours', type=int, default=168)
	parser.set_defaults(command=handle_create_invite)


def add_add_room_member_parser(subparsers):
	'''
	Add the add-room-member subcommand parser.
	'''

	parser = subparsers.add_parser('add-room-member')
	parser.add_argument('--actor-user-id', required=True)
	parser.add_argument('--role', choices=sorted(rooms.ROOM_ROLES), default='member')
	parser.add_argument('--room-id', required=True)
	parser.add_argument('--user-id', required=True)
	parser.set_defaults(command=handle_add_room_member)


def add_can_access_room_parser(subparsers):
	'''
	Add the can-access-room subcommand parser.
	'''

	parser = subparsers.add_parser('can-access-room')
	parser.add_argument('--room-id', required=True)
	parser.add_argument('--user-id', required=True)
	parser.set_defaults(command=handle_can_access_room)


def add_create_room_parser(subparsers):
	'''
	Add the create-room subcommand parser.
	'''

	parser = subparsers.add_parser('create-room')
	parser.add_argument('--actor-user-id', required=True)
	parser.add_argument('--group-id')
	parser.add_argument('--name', required=True)
	parser.add_argument('--scope', choices=sorted(rooms.ROOM_SCOPES), required=True)
	parser.add_argument('--slug', required=True)
	parser.add_argument('--xmpp-room-jid')
	parser.set_defaults(command=handle_create_room)


def add_change_room_access_parser(subparsers):
	'''
	Add the change-room-access subcommand parser.
	'''

	parser = subparsers.add_parser('change-room-access')
	parser.add_argument('--actor-user-id', required=True)
	parser.add_argument('--group-id')
	parser.add_argument('--room-id', required=True)
	parser.add_argument('--scope', choices=sorted(rooms.ROOM_SCOPES), required=True)
	parser.set_defaults(command=handle_change_room_access)


def add_list_invites_parser(subparsers):
	'''
	Add the list-invites subcommand parser.
	'''

	parser = subparsers.add_parser('list-invites')
	parser.set_defaults(command=handle_list_invites)


def add_list_rooms_parser(subparsers):
	'''
	Add the list-rooms subcommand parser.
	'''

	parser = subparsers.add_parser('list-rooms')
	parser.set_defaults(command=handle_list_rooms)


def add_migrate_parser(subparsers):
	'''
	Add the migrate subcommand parser.
	'''

	parser = subparsers.add_parser('migrate')
	parser.set_defaults(command=handle_migrate)


def add_list_verifications_parser(subparsers):
	'''
	Add the list-verifications subcommand parser.
	'''

	parser = subparsers.add_parser('list-verifications')
	parser.add_argument('--status')
	parser.add_argument('--user-id')
	parser.set_defaults(command=handle_list_verifications)


def add_approve_verification_parser(subparsers):
	'''
	Add the approve-verification subcommand parser.
	'''

	parser = subparsers.add_parser('approve-verification')
	parser.add_argument('--admin-user-id', required=True)
	parser.add_argument('--reason')
	parser.add_argument('--request-id', required=True)
	parser.set_defaults(command=handle_approve_verification)


def add_reject_verification_parser(subparsers):
	'''
	Add the reject-verification subcommand parser.
	'''

	parser = subparsers.add_parser('reject-verification')
	parser.add_argument('--admin-user-id', required=True)
	parser.add_argument('--reason', required=True)
	parser.add_argument('--request-id', required=True)
	parser.set_defaults(command=handle_reject_verification)


def add_redeem_invite_parser(subparsers):
	'''
	Add the redeem-invite subcommand parser.
	'''

	parser = subparsers.add_parser('redeem-invite')
	parser.add_argument('--display-name', required=True)
	parser.add_argument('--email')
	parser.add_argument('--token', required=True)
	parser.add_argument('--xmpp-jid')
	parser.set_defaults(command=handle_redeem_invite)


def add_remove_room_member_parser(subparsers):
	'''
	Add the remove-room-member subcommand parser.
	'''

	parser = subparsers.add_parser('remove-room-member')
	parser.add_argument('--actor-user-id', required=True)
	parser.add_argument('--room-id', required=True)
	parser.add_argument('--user-id', required=True)
	parser.set_defaults(command=handle_remove_room_member)


def add_submit_verification_parser(subparsers):
	'''
	Add the submit-verification subcommand parser.
	'''

	parser = subparsers.add_parser('submit-verification')
	parser.add_argument('--group-id')
	parser.add_argument('--note')
	parser.add_argument('--type', choices=sorted(verifications.ROLE_BY_REQUEST_TYPE), required=True)
	parser.add_argument('--user-id', required=True)
	parser.set_defaults(command=handle_submit_verification)


def add_revoke_invite_parser(subparsers):
	'''
	Add the revoke-invite subcommand parser.
	'''

	parser = subparsers.add_parser('revoke-invite')
	parser.add_argument('--actor-user-id', required=True)
	parser.add_argument('--invite-id', required=True)
	parser.set_defaults(command=handle_revoke_invite)


def build_parser() -> argparse.ArgumentParser:
	'''
	Build the portal CLI argument parser.
	'''

	parser     = argparse.ArgumentParser(prog='orthodox-connect-portal')
	subparsers = parser.add_subparsers(dest='command_name')

	add_add_room_member_parser(subparsers)
	add_can_access_room_parser(subparsers)
	add_change_room_access_parser(subparsers)
	add_create_invite_parser(subparsers)
	add_create_room_parser(subparsers)
	add_list_invites_parser(subparsers)
	add_list_rooms_parser(subparsers)
	add_list_verifications_parser(subparsers)
	add_migrate_parser(subparsers)
	add_approve_verification_parser(subparsers)
	add_reject_verification_parser(subparsers)
	add_redeem_invite_parser(subparsers)
	add_remove_room_member_parser(subparsers)
	add_revoke_invite_parser(subparsers)
	add_submit_verification_parser(subparsers)

	return parser


def handle_add_room_member(args):
	'''
	Handle add-room-member command execution.

	:param args: Parsed command arguments
	'''

	print_json(rooms.add_room_membership(args.room_id, args.user_id, args.actor_user_id, args.role))


def handle_can_access_room(args):
	'''
	Handle can-access-room command execution.

	:param args: Parsed command arguments
	'''

	print_json({'allowed': rooms.can_access_room(args.room_id, args.user_id)})


def handle_change_room_access(args):
	'''
	Handle change-room-access command execution.

	:param args: Parsed command arguments
	'''

	print_json(rooms.change_room_access(args.actor_user_id, args.room_id, args.scope, args.group_id))


def handle_create_invite(args):
	'''
	Handle create-invite command execution.

	:param args: Parsed command arguments
	'''

	expires_at = parse_expiry(args.expires_at, args.ttl_hours)
	invite     = invites.create_invite(
		created_by_user_id=args.created_by_user_id,
		expected_role_id=args.expected_role_id,
		expires_at=expires_at,
		group_id=args.group_id,
		reusable=args.reusable
	)

	print_json(invite)


def handle_create_room(args):
	'''
	Handle create-room command execution.

	:param args: Parsed command arguments
	'''

	print_json(
		rooms.create_room(
			actor_user_id=args.actor_user_id,
			group_id=args.group_id,
			name=args.name,
			privacy_level=args.scope,
			slug=args.slug,
			xmpp_room_jid=args.xmpp_room_jid
		)
	)


def handle_approve_verification(args):
	'''
	Handle approve-verification command execution.

	:param args: Parsed command arguments
	'''

	print_json(verifications.approve_request(args.request_id, args.admin_user_id, args.reason))


def handle_list_invites(args):
	'''
	Handle list-invites command execution.

	:param args: Parsed command arguments
	'''

	print_json(invites.list_invites())


def handle_list_rooms(args):
	'''
	Handle list-rooms command execution.

	:param args: Parsed command arguments
	'''

	print_json(rooms.list_rooms())


def handle_list_verifications(args):
	'''
	Handle list-verifications command execution.

	:param args: Parsed command arguments
	'''

	print_json(verifications.list_requests(args.status, args.user_id))


def handle_migrate(args):
	'''
	Handle migrate command execution.

	:param args: Parsed command arguments
	'''

	print_json({'applied': migrations.apply_migrations()})


def handle_reject_verification(args):
	'''
	Handle reject-verification command execution.

	:param args: Parsed command arguments
	'''

	print_json(verifications.reject_request(args.request_id, args.admin_user_id, args.reason))


def handle_redeem_invite(args):
	'''
	Handle redeem-invite command execution.

	:param args: Parsed command arguments
	'''

	result = invites.redeem_invite(
		display_name=args.display_name,
		email=args.email,
		token=args.token,
		xmpp_jid=args.xmpp_jid
	)

	print_json(result)


def handle_remove_room_member(args):
	'''
	Handle remove-room-member command execution.

	:param args: Parsed command arguments
	'''

	print_json(rooms.remove_room_membership(args.room_id, args.user_id, args.actor_user_id))


def handle_submit_verification(args):
	'''
	Handle submit-verification command execution.

	:param args: Parsed command arguments
	'''

	print_json(verifications.create_request(args.user_id, args.type, args.group_id, args.note))


def handle_revoke_invite(args):
	'''
	Handle revoke-invite command execution.

	:param args: Parsed command arguments
	'''

	print_json(invites.revoke_invite(args.invite_id, args.actor_user_id))


def main() -> int:
	'''
	Run the portal CLI.
	'''

	parser = build_parser()
	args   = parser.parse_args()

	if not hasattr(args, 'command'):
		parser.print_help()

		return 1

	try:
		args.command(args)
	except (invites.InviteError, rooms.RoomAccessError, verifications.VerificationError) as e:
		print_json({'error': str(e)})

		return 1

	return 0


def parse_expiry(expires_at: str | None, ttl_hours: int) -> datetime:
	'''
	Return an expiration timestamp from an ISO value or TTL.

	:param expires_at: Optional ISO timestamp
	:param ttl_hours: Hours from now when no timestamp is supplied
	'''

	if expires_at:
		parsed = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))

		if parsed.tzinfo:
			return parsed

		return parsed.replace(tzinfo=timezone.utc)

	return datetime.now(timezone.utc) + timedelta(hours=ttl_hours)


def print_json(data):
	'''
	Print JSON with stable formatting.

	:param data: JSON-serializable value
	'''

	print(json.dumps(data, default=str, indent=2, sort_keys=True))


if __name__ == '__main__':
	sys.exit(main())
