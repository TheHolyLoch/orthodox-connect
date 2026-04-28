#!/usr/bin/env python3
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/app/admin.py

import html
import http.cookies
import json
import os
import urllib.parse

from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from portal.app import auth, config, db, invites, rooms, verifications


ADMIN_ROLES = rooms.ADMIN_ROLES


class AdminUiError(Exception):
	'''Base exception for admin UI failures.'''


class AdminAuthorizationError(AdminUiError):
	'''Raised when an actor is not authorized for admin UI actions.'''


class AdminRequestHandler(BaseHTTPRequestHandler):
	'''Serve the minimal Orthodox Connect admin UI.'''

	def do_GET(self):
		'''Handle admin UI GET requests.'''

		route, query = parse_request_path(self.path)

		if route == '/healthz':
			self.send_health()

			return

		if route == '/admin.css':
			self.send_css()

			return

		if route == '/login':
			self.send_html(render_login_page(single_value(query, 'message')))

			return

		if route == '/logout':
			self.redirect('/login?message=Signed%20out', clear_session=True)

			return

		if route == '/':
			self.redirect('/admin')

			return

		if route != '/admin':
			self.send_error(404)

			return

		current_user = self.current_admin_user()

		if not current_user:
			self.redirect('/login')

			return

		self.send_html(render_admin_page(current_user, query))

	def do_POST(self):
		'''Handle admin UI POST actions.'''

		route, query = parse_request_path(self.path)
		form         = parse_form(self)

		if route == '/login':
			self.handle_login(form)

			return

		if route == '/logout':
			self.redirect('/login?message=Signed%20out', clear_session=True)

			return

		current_user = self.current_admin_user()

		if not current_user:
			self.redirect('/login')

			return

		actor_id = str(current_user['id'])

		try:
			if route == '/admin/invites/create':
				invite = handle_create_invite(form, actor_id)
				message = f'Invite created. Token: {invite["token"]}'
			elif route == '/admin/invites/revoke':
				handle_revoke_invite(form, actor_id)
				message = 'Invite revoked.'
			elif route == '/admin/verifications/approve':
				handle_approve_verification(form, actor_id)
				message = 'Verification approved.'
			elif route == '/admin/verifications/reject':
				handle_reject_verification(form, actor_id)
				message = 'Verification rejected.'
			else:
				self.send_error(404)

				return
		except (AdminUiError, invites.InviteError, verifications.VerificationError) as error:
			message = f'Error: {error}'

		self.send_html(render_admin_page(current_user, {'message': [message]}))

	def current_admin_user(self) -> dict | None:
		'''Return the authenticated admin user for the current request.'''

		cookie_header = self.headers.get('Cookie', '')
		cookies       = http.cookies.SimpleCookie(cookie_header)
		session       = cookies.get(auth.SESSION_COOKIE)

		return auth.load_session_user(session.value if session else None)

	def handle_login(self, form: dict):
		'''
		Handle admin login form submission.

		:param form: Parsed form data
		'''

		email    = single_value(form, 'email')
		password = single_value(form, 'password')
		result   = auth.login(email, password, self.client_address[0] if self.client_address else '')

		if not result:
			self.send_html(render_login_page('Login failed.'), status_code=401)

			return

		self.send_response(303)
		self.send_header('Location', '/admin')
		self.send_header('Set-Cookie', session_cookie(result['session']))
		self.end_headers()

	def log_message(self, format, *args):
		'''Keep request logs minimal for local operation.'''

		return

	def send_css(self):
		'''Send the admin stylesheet.'''

		self.send_response(200)
		self.send_header('Content-Type', 'text/css; charset=utf-8')
		self.end_headers()
		self.wfile.write(admin_css().encode('utf-8'))

	def redirect(self, location: str, clear_session: bool = False):
		'''
		Send a redirect response.

		:param location: Redirect target
		:param clear_session: Whether to clear the session cookie
		'''

		self.send_response(303)
		self.send_header('Location', location)

		if clear_session:
			self.send_header('Set-Cookie', f'{auth.SESSION_COOKIE}=; HttpOnly; Path=/; SameSite=Lax; Max-Age=0')

		self.end_headers()

	def send_html(self, body: str, status_code: int = 200):
		'''Send an HTML response.

		:param body: Response body
		:param status_code: HTTP status code
		'''

		self.send_response(status_code)
		self.send_header('Content-Type', 'text/html; charset=utf-8')
		self.end_headers()
		self.wfile.write(body.encode('utf-8'))

	def send_health(self):
		'''Send portal health status.'''

		status_code = 200
		payload     = {
			'database': 'ok',
			'service': 'portal',
			'status': 'ok',
		}

		try:
			with db.connect_database() as connection:
				with connection.cursor() as cursor:
					cursor.execute('SELECT 1 AS ok')
					cursor.fetchone()
		except Exception as error:
			status_code          = 503
			payload['database'] = 'error'
			payload['error']    = error.__class__.__name__
			payload['status']   = 'error'

		self.send_response(status_code)
		self.send_header('Content-Type', 'application/json; charset=utf-8')
		self.end_headers()
		self.wfile.write(json.dumps(payload, sort_keys=True).encode('utf-8'))


def admin_css() -> str:
	'''Return the admin UI stylesheet.'''

	return '''
* {
	box-sizing: border-box;
}

body {
	margin: 0;
	background: #f6f2ea;
	color: #1d2625;
	font-family: Georgia, 'Times New Roman', serif;
}

a {
	color: #245b55;
}

button,
input,
select,
textarea {
	font: inherit;
}

button,
.button {
	background: #245b55;
	border: 0;
	border-radius: 4px;
	color: #fff;
	cursor: pointer;
	padding: 0.55rem 0.8rem;
}

button.secondary {
	background: #5d5144;
}

form.inline {
	display: inline;
}

header {
	background: #203634;
	color: #fff;
	padding: 1.25rem clamp(1rem, 4vw, 3rem);
}

main {
	margin: 0 auto;
	max-width: 1280px;
	padding: 1.25rem;
}

section {
	background: #fffdf8;
	border: 1px solid #d9d0c2;
	border-radius: 6px;
	margin: 0 0 1rem;
	padding: 1rem;
}

h1,
h2 {
	margin: 0;
}

h1 {
	font-size: 1.8rem;
}

h2 {
	font-size: 1.1rem;
	margin-bottom: 0.75rem;
}

.actor,
.login,
.message {
	display: grid;
	gap: 0.75rem;
	grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.message {
	background: #edf3ed;
	border-color: #bacfba;
}

.error {
	background: #f7e7e4;
	border-color: #d8aaa2;
}

.forms {
	display: grid;
	gap: 1rem;
	grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.field {
	display: flex;
	flex-direction: column;
	gap: 0.3rem;
	margin-bottom: 0.65rem;
}

.field.checkbox {
	align-items: center;
	flex-direction: row;
}

input,
select,
textarea {
	background: #fff;
	border: 1px solid #bdb3a4;
	border-radius: 4px;
	padding: 0.45rem 0.55rem;
	width: 100%;
}

label {
	font-weight: 700;
}

.table-wrap {
	overflow-x: auto;
}

table {
	border-collapse: collapse;
	min-width: 760px;
	width: 100%;
}

th,
td {
	border-bottom: 1px solid #e6ded2;
	padding: 0.5rem;
	text-align: left;
	vertical-align: top;
}

th {
	background: #efe7da;
	font-size: 0.9rem;
}

.muted {
	color: #65706f;
}

.token {
	font-family: 'Courier New', monospace;
	font-size: 0.82rem;
	word-break: break-all;
}
'''


def fetch_admin_state(actor_id: str | None) -> dict:
	'''
	Return all data needed by the admin UI.

	:param actor_id: Optional acting admin user ID
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			authorized = is_admin(cursor, actor_id)

			if not authorized:
				return {
					'authorized': False,
					'audit_events': [],
					'groups': [],
					'invites': [],
					'roles': [],
					'rooms': [],
					'users': [],
					'verification_requests': [],
				}

			return {
				'authorized': True,
				'audit_events': list_audit_events(cursor),
				'groups': list_groups(cursor),
				'invites': list_invites(cursor),
				'roles': list_roles(cursor),
				'rooms': list_rooms(cursor),
				'users': list_users(cursor),
				'verification_requests': verifications.list_requests(),
			}


def handle_approve_verification(form: dict, actor_id: str | None):
	'''
	Approve a verification request from the admin UI.

	:param form: Parsed POST form
	:param actor_id: Acting admin user ID
	'''

	require_admin(actor_id)
	verifications.approve_request(single_value(form, 'request_id'), actor_id, optional_value(form, 'reason'))


def handle_create_invite(form: dict, actor_id: str | None) -> dict:
	'''
	Create an invite from the admin UI.

	:param form: Parsed POST form
	:param actor_id: Acting admin user ID
	'''

	require_admin(actor_id)

	ttl_hours  = int(single_value(form, 'ttl_hours') or '168')
	expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

	return invites.create_invite(
		created_by_user_id=actor_id,
		expected_role_id=optional_value(form, 'expected_role_id'),
		expires_at=expires_at,
		group_id=optional_value(form, 'group_id'),
		reusable=single_value(form, 'reusable') == 'on'
	)


def handle_reject_verification(form: dict, actor_id: str | None):
	'''
	Reject a verification request from the admin UI.

	:param form: Parsed POST form
	:param actor_id: Acting admin user ID
	'''

	require_admin(actor_id)
	verifications.reject_request(single_value(form, 'request_id'), actor_id, single_value(form, 'reason'))


def handle_revoke_invite(form: dict, actor_id: str | None):
	'''
	Revoke an invite from the admin UI.

	:param form: Parsed POST form
	:param actor_id: Acting admin user ID
	'''

	require_admin(actor_id)
	invites.revoke_invite(single_value(form, 'invite_id'), actor_id)


def is_admin(cursor, actor_id: str | None) -> bool:
	'''
	Return whether an actor has an admin role.

	:param cursor: Open database cursor
	:param actor_id: Acting admin user ID
	'''

	if not actor_id:
		return False

	user = rooms.fetch_user(cursor, actor_id)

	if not user or user['status'] != 'approved':
		return False

	return rooms.has_any_scoped_role(cursor, actor_id, ADMIN_ROLES)


def list_audit_events(cursor) -> list[dict]:
	'''
	Return recent audit events.

	:param cursor: Open database cursor
	'''

	cursor.execute(
		'''
		SELECT
			id,
			actor_user_id,
			target_user_id,
			entity_type,
			entity_id,
			action,
			scope_group_id,
			metadata,
			created_at
		FROM audit_events
		ORDER BY created_at DESC
		LIMIT 100
		'''
	)

	return cursor.fetchall()


def list_groups(cursor) -> list[dict]:
	'''
	Return groups and parishes.

	:param cursor: Open database cursor
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
		ORDER BY name ASC
		'''
	)

	return cursor.fetchall()


def list_invites(cursor) -> list[dict]:
	'''
	Return invite records.

	:param cursor: Open database cursor
	'''

	cursor.execute(
		'''
		SELECT
			id,
			created_by_user_id,
			group_id,
			expected_role_id,
			status,
			expires_at,
			reusable,
			use_count,
			accepted_by_user_id,
			accepted_at,
			created_at,
			updated_at
		FROM invites
		ORDER BY created_at DESC
		'''
	)

	return cursor.fetchall()


def list_roles(cursor) -> list[dict]:
	'''
	Return roles.

	:param cursor: Open database cursor
	'''

	cursor.execute(
		'''
		SELECT
			id,
			name,
			description,
			created_at
		FROM roles
		ORDER BY name ASC
		'''
	)

	return cursor.fetchall()


def list_rooms(cursor) -> list[dict]:
	'''
	Return rooms and channels.

	:param cursor: Open database cursor
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
			privacy_level,
			created_at,
			updated_at
		FROM rooms
		ORDER BY created_at DESC
		'''
	)

	return cursor.fetchall()


def list_users(cursor) -> list[dict]:
	'''
	Return portal users.

	:param cursor: Open database cursor
	'''

	cursor.execute(
		'''
		SELECT
			u.id,
			u.display_name,
			u.email,
			u.xmpp_jid,
			u.status,
			u.created_at,
			u.updated_at,
			COALESCE(string_agg(DISTINCT r.name, ', ' ORDER BY r.name), '') AS roles,
			COALESCE(string_agg(DISTINCT g.name, ', ' ORDER BY g.name), '') AS groups
		FROM users u
		LEFT JOIN user_roles ur ON ur.user_id = u.id
			AND ur.revoked_at IS NULL
		LEFT JOIN roles r ON r.id = ur.role_id
		LEFT JOIN group_memberships gm ON gm.user_id = u.id
			AND gm.status = 'active'
		LEFT JOIN groups g ON g.id = gm.group_id
		GROUP BY u.id
		ORDER BY u.created_at DESC
		'''
	)

	return cursor.fetchall()


def main():
	'''Run the admin UI server.'''

	host   = os.getenv('PORTAL_ADMIN_HOST', '0.0.0.0')
	port   = int(os.getenv('PORTAL_ADMIN_PORT', '8000'))
	server = ThreadingHTTPServer((host, port), AdminRequestHandler)
	server.serve_forever()


def optional_value(form: dict, name: str) -> str | None:
	'''
	Return an optional form value.

	:param form: Parsed form data
	:param name: Field name
	'''

	value = single_value(form, name)

	return value or None


def parse_form(handler: BaseHTTPRequestHandler) -> dict:
	'''
	Return parsed URL-encoded POST form data.

	:param handler: HTTP request handler
	'''

	length = int(handler.headers.get('Content-Length', '0'))
	body   = handler.rfile.read(length).decode('utf-8')

	return urllib.parse.parse_qs(body)


def parse_request_path(path: str) -> tuple[str, dict]:
	'''
	Return route path and parsed query data.

	:param path: Raw request path
	'''

	parsed = urllib.parse.urlparse(path)

	return parsed.path, urllib.parse.parse_qs(parsed.query)


def render_admin_session(current_user: dict) -> str:
	'''
	Return current admin session markup.

	:param current_user: Authenticated admin user
	'''

	return f'''
<section>
	<form class="actor" method="post" action="/logout">
		<p><strong>{escape(current_user['display_name'])}</strong><br><span class="muted">{escape(current_user['email'] or '')}</span></p>
		<button class="secondary" type="submit">Logout</button>
	</form>
</section>
'''


def render_admin_page(current_user: dict, query: dict) -> str:
	'''
	Return the admin UI HTML.

	:param current_user: Authenticated admin user
	:param query: Parsed query data
	'''

	actor_id = str(current_user['id'])
	message  = single_value(query, 'message')
	state    = fetch_admin_state(actor_id)
	content  = [
		'<!doctype html>',
		'<html lang="en">',
		'<head>',
		'<meta charset="utf-8">',
		'<meta name="viewport" content="width=device-width, initial-scale=1">',
		'<title>Orthodox Connect Admin</title>',
		'<link rel="stylesheet" href="/admin.css">',
		'</head>',
		'<body>',
		'<header><h1>Orthodox Connect Admin</h1><p>Invite, verification, room, and audit workflow</p></header>',
		'<main>',
		render_admin_session(current_user),
	]

	if message:
		class_name = 'message error' if message.startswith('Error:') else 'message'
		content.append(f'<section class="{class_name}">{escape(message)}</section>')

	if not state['authorized']:
		content.append('<section class="error">Enter an approved admin user ID with an assigned admin role to view or change portal data.</section>')
	else:
		content.extend([
			render_invite_management(actor_id, state),
			render_verification_management(actor_id, state),
			render_users(state['users']),
			render_groups(state['groups']),
			render_roles(state['roles']),
			render_rooms(state['rooms']),
			render_audit_events(state['audit_events']),
		])

	content.extend(['</main>', '</body>', '</html>'])

	return '\n'.join(content)


def render_audit_events(audit_events: list[dict]) -> str:
	'''
	Return audit event table markup.

	:param audit_events: Audit event records
	'''

	return render_table(
		'Audit Events',
		audit_events,
		['created_at', 'action', 'entity_type', 'entity_id', 'actor_user_id', 'target_user_id', 'scope_group_id', 'metadata']
	)


def render_groups(groups: list[dict]) -> str:
	'''
	Return group table markup.

	:param groups: Group records
	'''

	return render_table('Groups and Parishes', groups, ['name', 'slug', 'group_type', 'parent_group_id', 'description', 'created_at'])


def render_login_page(message: str | None = None) -> str:
	'''
	Return the admin login page.

	:param message: Optional status message
	'''

	content = [
		'<!doctype html>',
		'<html lang="en">',
		'<head>',
		'<meta charset="utf-8">',
		'<meta name="viewport" content="width=device-width, initial-scale=1">',
		'<title>Orthodox Connect Login</title>',
		'<link rel="stylesheet" href="/admin.css">',
		'</head>',
		'<body>',
		'<header><h1>Orthodox Connect Admin</h1><p>Local portal login</p></header>',
		'<main>',
	]

	if message:
		class_name = 'message error' if 'failed' in message.lower() else 'message'
		content.append(f'<section class="{class_name}">{escape(message)}</section>')

	content.append(
		'''
<section>
	<form class="login" method="post" action="/login">
		<div class="field">
			<label for="email">Email</label>
			<input id="email" name="email" type="email" autocomplete="username" required>
		</div>
		<div class="field">
			<label for="password">Password</label>
			<input id="password" name="password" type="password" autocomplete="current-password" required>
		</div>
		<div class="field">
			<label>&nbsp;</label>
			<button type="submit">Login</button>
		</div>
	</form>
</section>
'''
	)
	content.extend(['</main>', '</body>', '</html>'])

	return '\n'.join(content)


def render_invite_management(actor_id: str | None, state: dict) -> str:
	'''
	Return invite management section markup.

	:param actor_id: Acting admin user ID
	:param state: Admin page state
	'''

	role_options  = options_markup(state['roles'], 'id', 'name')
	group_options = options_markup(state['groups'], 'id', 'name')
	rows          = []

	for invite in state['invites']:
		action = ''

		if invite['status'] == 'unused':
			action = f'''
<form class="inline" method="post" action="/admin/invites/revoke">
	<input type="hidden" name="invite_id" value="{escape(invite['id'])}">
	<button class="secondary" type="submit">Revoke</button>
</form>
'''

		row           = dict(invite)
		row['action'] = action
		rows.append(row)

	return f'''
<section>
	<h2>Invites</h2>
	<div class="forms">
		<form method="post" action="/admin/invites/create">
			<div class="field">
				<label for="group_id">Group scope</label>
				<select id="group_id" name="group_id"><option value="">No group scope</option>{group_options}</select>
			</div>
			<div class="field">
				<label for="expected_role_id">Expected role</label>
				<select id="expected_role_id" name="expected_role_id"><option value="">No expected role</option>{role_options}</select>
			</div>
			<div class="field">
				<label for="ttl_hours">Expires after hours</label>
				<input id="ttl_hours" name="ttl_hours" type="number" min="1" value="168">
			</div>
			<div class="field checkbox">
				<input id="reusable" name="reusable" type="checkbox">
				<label for="reusable">Reusable invite</label>
			</div>
			<button type="submit">Create Invite</button>
		</form>
	</div>
	{render_table('', rows, ['status', 'expires_at', 'reusable', 'use_count', 'group_id', 'expected_role_id', 'created_by_user_id', 'accepted_by_user_id', 'action'])}
</section>
'''


def render_roles(roles: list[dict]) -> str:
	'''
	Return roles table markup.

	:param roles: Role records
	'''

	return render_table('Roles', roles, ['name', 'description', 'created_at'])


def render_rooms(room_records: list[dict]) -> str:
	'''
	Return rooms table markup.

	:param room_records: Room records
	'''

	return render_table('Rooms and Channels', room_records, ['name', 'slug', 'privacy_level', 'group_id', 'xmpp_room_jid', 'created_by_user_id', 'created_at'])


def render_table(title: str, rows: list[dict], columns: list[str]) -> str:
	'''
	Return a table for row dictionaries.

	:param title: Section title
	:param rows: Row dictionaries
	:param columns: Column names
	'''

	heading = f'<h2>{escape(title)}</h2>' if title else ''

	if not rows:
		return f'{heading}<p class="muted">No records.</p>'

	headers = ''.join(f'<th>{escape(column.replace("_", " ").title())}</th>' for column in columns)
	body    = []

	for row in rows:
		cells = ''.join(f'<td>{render_value(row.get(column))}</td>' for column in columns)
		body.append(f'<tr>{cells}</tr>')

	return f'{heading}<div class="table-wrap"><table><thead><tr>{headers}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def render_users(users: list[dict]) -> str:
	'''
	Return users table markup.

	:param users: User records
	'''

	return render_table('Users', users, ['display_name', 'email', 'xmpp_jid', 'status', 'roles', 'groups', 'created_at'])


def render_value(value) -> str:
	'''
	Return escaped table cell content.

	:param value: Raw value
	'''

	if value is None:
		return '<span class="muted">-</span>'

	if isinstance(value, dict):
		return f'<span class="token">{escape(json.dumps(value, sort_keys=True))}</span>'

	return escape(value)


def render_verification_management(actor_id: str | None, state: dict) -> str:
	'''
	Return verification management section markup.

	:param actor_id: Acting admin user ID
	:param state: Admin page state
	'''

	rows = []

	for request in state['verification_requests']:
		action = ''

		if request['status'] == 'pending':
			action = f'''
<form class="inline" method="post" action="/admin/verifications/approve">
	<input type="hidden" name="request_id" value="{escape(request['id'])}">
	<button type="submit">Approve</button>
</form>
<form class="inline" method="post" action="/admin/verifications/reject">
	<input type="hidden" name="request_id" value="{escape(request['id'])}">
	<input name="reason" placeholder="Rejection reason" required>
	<button class="secondary" type="submit">Reject</button>
</form>
'''

		row           = dict(request)
		row['action'] = action
		rows.append(row)

	return f'''
<section>
	<h2>Verification Requests</h2>
	{render_table('', rows, ['status', 'request_type', 'user_id', 'group_id', 'note', 'decision', 'reason', 'created_at', 'decided_at', 'action'])}
</section>
'''


def escape(value) -> str:
	'''
	Return HTML escaped text.

	:param value: Value to escape
	'''

	return html.escape(str(value), quote=True)


def options_markup(rows: list[dict], value_key: str, label_key: str) -> str:
	'''
	Return select option markup.

	:param rows: Option rows
	:param value_key: Row key for option value
	:param label_key: Row key for option label
	'''

	return ''.join(f'<option value="{escape(row[value_key])}">{escape(row[label_key])}</option>' for row in rows)


def require_admin(actor_id: str | None):
	'''
	Raise unless the actor has an admin role.

	:param actor_id: Acting admin user ID
	'''

	with db.connect_database() as connection:
		with connection.cursor() as cursor:
			if not is_admin(cursor, actor_id):
				raise AdminAuthorizationError('admin role required')


def session_cookie(session_token: str) -> str:
	'''
	Return the portal session cookie header value.

	:param session_token: Signed session token
	'''

	max_age = str(config.portal_session_ttl_seconds())

	return f'{auth.SESSION_COOKIE}={session_token}; HttpOnly; Path=/; SameSite=Lax; Max-Age={max_age}'


def single_value(values: dict, name: str) -> str:
	'''
	Return a single parsed query or form value.

	:param values: Parsed values
	:param name: Field name
	'''

	raw_value = values.get(name, [''])

	return raw_value[0].strip() if raw_value else ''


if __name__ == '__main__':
	main()
