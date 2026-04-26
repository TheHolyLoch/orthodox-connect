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
