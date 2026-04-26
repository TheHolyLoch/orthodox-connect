#!/usr/bin/env python3
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/cli.py

import argparse
import json
import sys

from datetime import datetime, timedelta, timezone

from portal.app import invites, migrations


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


def add_list_invites_parser(subparsers):
	'''
	Add the list-invites subcommand parser.
	'''

	parser = subparsers.add_parser('list-invites')
	parser.set_defaults(command=handle_list_invites)


def add_migrate_parser(subparsers):
	'''
	Add the migrate subcommand parser.
	'''

	parser = subparsers.add_parser('migrate')
	parser.set_defaults(command=handle_migrate)


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

	add_create_invite_parser(subparsers)
	add_list_invites_parser(subparsers)
	add_migrate_parser(subparsers)
	add_redeem_invite_parser(subparsers)
	add_revoke_invite_parser(subparsers)

	return parser


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


def handle_list_invites(args):
	'''
	Handle list-invites command execution.

	:param args: Parsed command arguments
	'''

	print_json(invites.list_invites())


def handle_migrate(args):
	'''
	Handle migrate command execution.

	:param args: Parsed command arguments
	'''

	print_json({'applied': migrations.apply_migrations()})


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
	except invites.InviteError as e:
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
