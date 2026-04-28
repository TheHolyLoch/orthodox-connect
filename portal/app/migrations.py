# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/migrations.py

import pathlib

from portal.app import db


MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parents[1] / 'migrations'


def apply_migrations() -> list[str]:
	'''
	Apply unapplied SQL migrations and return their filenames.
	'''

	applied = []

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			cursor.execute("SELECT to_regclass('public.users') AS users_table")
			initial_schema_exists = cursor.fetchone()['users_table'] is not None

			cursor.execute(
				'''
				CREATE TABLE IF NOT EXISTS schema_migrations (
					filename text PRIMARY KEY,
					applied_at timestamptz NOT NULL DEFAULT now()
				)
				'''
			)

			for migration_path in sorted(MIGRATIONS_DIR.glob('*.sql')):
				if migration_path.name == '001_initial_schema.sql' and initial_schema_exists:
					cursor.execute(
						'INSERT INTO schema_migrations (filename) VALUES (%s) ON CONFLICT (filename) DO NOTHING',
						(migration_path.name,)
					)
					continue

				if migration_path.name == '002_invite_workflow.sql' and migration_002_exists(cursor):
					cursor.execute(
						'INSERT INTO schema_migrations (filename) VALUES (%s) ON CONFLICT (filename) DO NOTHING',
						(migration_path.name,)
					)
					continue

				if migration_path.name == '003_manual_verification.sql' and migration_003_exists(cursor):
					cursor.execute(
						'INSERT INTO schema_migrations (filename) VALUES (%s) ON CONFLICT (filename) DO NOTHING',
						(migration_path.name,)
					)
					continue

				if migration_path.name == '004_room_access_model.sql' and migration_004_exists(cursor):
					cursor.execute(
						'INSERT INTO schema_migrations (filename) VALUES (%s) ON CONFLICT (filename) DO NOTHING',
						(migration_path.name,)
					)
					continue

				if migration_path.name == '005_jitsi_meeting_access.sql' and migration_005_exists(cursor):
					cursor.execute(
						'INSERT INTO schema_migrations (filename) VALUES (%s) ON CONFLICT (filename) DO NOTHING',
						(migration_path.name,)
					)
					continue

				if migration_path.name == '006_portal_authentication.sql' and migration_006_exists(cursor):
					cursor.execute(
						'INSERT INTO schema_migrations (filename) VALUES (%s) ON CONFLICT (filename) DO NOTHING',
						(migration_path.name,)
					)
					continue

				cursor.execute('SELECT 1 FROM schema_migrations WHERE filename = %s', (migration_path.name,))

				if cursor.fetchone():
					continue

				cursor.execute(migration_path.read_text())
				cursor.execute('INSERT INTO schema_migrations (filename) VALUES (%s)', (migration_path.name,))
				applied.append(migration_path.name)

		connection.commit()

	return applied


def migration_002_exists(cursor) -> bool:
	'''
	Return whether the invite workflow migration is already applied.

	:param cursor: Open database cursor
	'''

	cursor.execute(
		'''
		SELECT 1
		FROM information_schema.columns
		WHERE table_schema = 'public'
			AND table_name = 'invites'
			AND column_name = 'reusable'
		'''
	)

	return cursor.fetchone() is not None


def migration_003_exists(cursor) -> bool:
	'''
	Return whether the manual verification migration is already applied.

	:param cursor: Open database cursor
	'''

	cursor.execute(
		'''
		SELECT 1
		FROM pg_indexes
		WHERE schemaname = 'public'
			AND indexname = 'idx_verification_requests_request_type'
		'''
	)

	return cursor.fetchone() is not None


def migration_004_exists(cursor) -> bool:
	'''
	Return whether the room access model migration is already applied.

	:param cursor: Open database cursor
	'''

	cursor.execute(
		'''
		SELECT 1
		FROM information_schema.columns
		WHERE table_schema = 'public'
			AND table_name = 'rooms'
			AND column_name = 'created_by_user_id'
		'''
	)

	return cursor.fetchone() is not None


def migration_005_exists(cursor) -> bool:
	'''
	Return whether the Jitsi meeting access migration is already applied.

	:param cursor: Open database cursor
	'''

	cursor.execute("SELECT to_regclass('public.meetings') AS meetings_table")

	return cursor.fetchone()['meetings_table'] is not None


def migration_006_exists(cursor) -> bool:
	'''
	Return whether the portal authentication migration is already applied.

	:param cursor: Open database cursor
	'''

	cursor.execute(
		'''
		SELECT 1
		FROM information_schema.columns
		WHERE table_schema = 'public'
			AND table_name = 'users'
			AND column_name = 'password_hash'
		'''
	)

	return cursor.fetchone() is not None
