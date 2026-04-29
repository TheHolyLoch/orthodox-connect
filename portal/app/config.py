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


def env_or_file(name: str, default: str | None = None) -> str:
	'''
	Return an environment value, with Docker secret file fallback.

	:param name: Environment variable name
	:param default: Optional default value
	'''

	file_path = os.getenv(f'{name}_FILE')

	if file_path:
		with open(file_path, 'r', encoding='utf-8') as secret_file:
			return secret_file.read().strip()

	value = os.getenv(name)

	if value is not None:
		return value

	if default is not None:
		return default

	raise KeyError(name)


def database_url() -> str:
	'''
	Return the PostgreSQL database URL from the environment.
	'''

	configured_url = os.getenv('PORTAL_DATABASE_URL')

	if configured_url:
		return configured_url

	host     = env_or_file('POSTGRES_HOST', 'postgres')
	port     = env_or_file('POSTGRES_PORT', '5432')
	database = env_or_file('POSTGRES_DB')
	user     = env_or_file('POSTGRES_USER')
	password = env_or_file('POSTGRES_PASSWORD')

	return f'postgresql://{user}:{password}@{host}:{port}/{database}'


def invite_token_bytes() -> int:
	'''
	Return the byte length used for newly generated invite tokens.
	'''

	return int(os.getenv('PORTAL_INVITE_TOKEN_BYTES', '32'))


def portal_secret_key() -> str:
	'''
	Return the portal session signing secret.
	'''

	return env_or_file('PORTAL_SECRET_KEY')


def portal_session_ttl_seconds() -> int:
	'''
	Return the portal session lifetime in seconds.
	'''

	return int(os.getenv('PORTAL_SESSION_TTL_SECONDS', '28800'))


def jitsi_jwt_app_id() -> str:
	'''
	Return the Jitsi JWT application identifier.
	'''

	return os.environ['JITSI_JWT_APP_ID']


def jitsi_jwt_app_secret() -> str:
	'''
	Return the Jitsi JWT shared secret.
	'''

	return env_or_file('JITSI_JWT_APP_SECRET')


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

	return env_or_file('JITSI_PUBLIC_URL').rstrip('/')


def jitsi_token_ttl_seconds() -> int:
	'''
	Return the default Jitsi token lifetime in seconds.
	'''

	return int(os.getenv('JITSI_TOKEN_TTL_SECONDS', '3600'))


def jitsi_xmpp_domain() -> str:
	'''
	Return the Jitsi XMPP domain used in JWT subjects.
	'''

	return env_or_file('JITSI_XMPP_DOMAIN')


def xmpp_domain() -> str:
	'''
	Return the main Orthodox Connect XMPP domain.
	'''

	return env_or_file('XMPP_DOMAIN')


def xmpp_provisioning_token() -> str:
	'''
	Return the internal Prosody provisioning token.
	'''

	return env_or_file('XMPP_PROVISIONING_TOKEN')


def xmpp_provisioning_url() -> str:
	'''
	Return the internal Prosody provisioning endpoint URL.
	'''

	return env_or_file('XMPP_PROVISIONING_URL').rstrip('/')
