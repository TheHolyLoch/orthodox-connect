# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/db.py

try:
	import psycopg
	from psycopg.rows import dict_row
except ImportError:
	raise ImportError('missing psycopg library (pip install "psycopg[binary]")')

from portal.app import config


def connect_database():
	'''
	Open a PostgreSQL connection using the portal database URL.
	'''

	return psycopg.connect(config.database_url(), row_factory=dict_row)
