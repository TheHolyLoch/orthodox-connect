# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/config.py

import os


if os.path.exists('.env'):
	try:
		from dotenv import load_dotenv
	except ImportError:
		raise ImportError('missing python-dotenv library (pip install python-dotenv)')
	else:
		load_dotenv()


def database_url() -> str:
	'''
	Return the PostgreSQL database URL from the environment.
	'''

	return os.environ['PORTAL_DATABASE_URL']


def invite_token_bytes() -> int:
	'''
	Return the byte length used for newly generated invite tokens.
	'''

	return int(os.getenv('PORTAL_INVITE_TOKEN_BYTES', '32'))


def jitsi_jwt_app_id() -> str:
	'''
	Return the Jitsi JWT application identifier.
	'''

	return os.environ['JITSI_JWT_APP_ID']


def jitsi_jwt_app_secret() -> str:
	'''
	Return the Jitsi JWT shared secret.
	'''

	return os.environ['JITSI_JWT_APP_SECRET']


def jitsi_meeting_creator_roles() -> set[str]:
	'''
	Return role names allowed to create official Jitsi meetings.
	'''

	raw_roles = os.getenv('JITSI_MEETING_CREATOR_ROLES', 'parish_admin,diocesan_admin,platform_admin,clergy_verified')

	return {role.strip() for role in raw_roles.split(',') if role.strip()}


def jitsi_public_url() -> str:
	'''
	Return the public Jitsi URL.
	'''

	return os.environ['JITSI_PUBLIC_URL'].rstrip('/')


def jitsi_token_ttl_seconds() -> int:
	'''
	Return the default Jitsi token lifetime in seconds.
	'''

	return int(os.getenv('JITSI_TOKEN_TTL_SECONDS', '3600'))


def jitsi_xmpp_domain() -> str:
	'''
	Return the Jitsi XMPP domain used in JWT subjects.
	'''

	return os.environ['JITSI_XMPP_DOMAIN']
