#!/usr/bin/env bash
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/scripts/check-stack.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [ -f .env ]; then
	ENV_FILE=.env
	source .env
else
	ENV_FILE=.env.example
	source .env.example
fi

LOCAL_PROXY_SCHEME="${LOCAL_PROXY_SCHEME:-http}"
LOCAL_PROXY_PORT="${LOCAL_PROXY_PORT:-${HTTP_PORT:-8081}}"
PORTAL_DOMAIN="${PORTAL_DOMAIN:-portal.orthodox-connect.localhost}"
CHAT_DOMAIN="${CHAT_DOMAIN:-chat.orthodox-connect.localhost}"
MEET_DOMAIN="${MEET_DOMAIN:-meet.orthodox-connect.localhost}"

check_url() {
	local name="$1"
	local host="$2"
	local path="$3"

	if curl -kfsS --resolve "${host}:${LOCAL_PROXY_PORT}:127.0.0.1" "${LOCAL_PROXY_SCHEME}://${host}:${LOCAL_PROXY_PORT}${path}" >/dev/null; then
		echo "ok: ${name}"
	else
		echo "error: ${name}"
		return 1
	fi
}

check_route_status() {
	local name="$1"
	local host="$2"
	local path="$3"
	local status

	status="$(curl -k -sS -o /dev/null -w '%{http_code}' --resolve "${host}:${LOCAL_PROXY_PORT}:127.0.0.1" "${LOCAL_PROXY_SCHEME}://${host}:${LOCAL_PROXY_PORT}${path}")"

	case "${status}" in
		2*|3*|4*)
			echo "ok: ${name} (${status})"
			;;
		*)
			echo "error: ${name} (${status})"
			return 1
			;;
	esac
}

check_admin_denied() {
	local status

	status="$(curl -k -sS -o /dev/null -w '%{http_code}' --resolve "${PORTAL_DOMAIN}:${LOCAL_PROXY_PORT}:127.0.0.1" "${LOCAL_PROXY_SCHEME}://${PORTAL_DOMAIN}:${LOCAL_PROXY_PORT}/admin")"

	case "${status}" in
		30*|401|403)
			echo "ok: unauthenticated admin route denied (${status})"
			;;
		*)
			echo "error: unauthenticated admin route denied (${status})"
			return 1
			;;
	esac
}

check_converse_registration_hidden() {
	if docker compose --env-file "${ENV_FILE}" exec -T converse sh -c "grep -q \"registration_domain: ''\" /usr/share/nginx/html/config.js"; then
		echo "ok: converse registration disabled"
	else
		echo "error: converse registration disabled"
		return 1
	fi
}

check_federation_disabled() {
	if docker compose --env-file "${ENV_FILE}" exec -T prosody sh -c "grep -q \"'s2s'\" /etc/prosody/prosody.cfg.lua && grep -q 's2s_ports = { }' /etc/prosody/prosody.cfg.lua"; then
		echo "ok: prosody federation disabled"
	else
		echo "error: prosody federation disabled"
		return 1
	fi
}

check_security_headers() {
	if curl -kfsS -D - -o /dev/null --resolve "${PORTAL_DOMAIN}:${LOCAL_PROXY_PORT}:127.0.0.1" "${LOCAL_PROXY_SCHEME}://${PORTAL_DOMAIN}:${LOCAL_PROXY_PORT}/healthz" | grep -qi '^X-Content-Type-Options: nosniff'; then
		echo "ok: reverse proxy security headers"
	else
		echo "error: reverse proxy security headers"
		return 1
	fi
}

check_unpublished_port() {
	local service="$1"
	local port="$2"
	local container_id
	local published

	container_id="$(docker compose --env-file "${ENV_FILE}" ps -q "${service}")"
	published="$(docker container inspect "${container_id}" --format "{{with index .NetworkSettings.Ports \"${port}/tcp\"}}{{range .}}{{.HostIp}}:{{.HostPort}} {{end}}{{end}}")"

	if [ -n "${published}" ]; then
		echo "error: ${service} port ${port} is published"
		return 1
	fi

	echo "ok: ${service} port ${port} is internal-only"
}

check_postgres_bind() {
	local published

	published="$(docker compose --env-file "${ENV_FILE}" port postgres 5432 2>/dev/null || true)"

	case "${published}" in
		127.0.0.1:*|localhost:*|'')
			echo "ok: postgres host port is local-only"
			;;
		*)
			echo "error: postgres host port is not local-only (${published})"
			return 1
			;;
	esac
}

docker compose --env-file "${ENV_FILE}" ps

check_url "portal health" "${PORTAL_DOMAIN}" "/healthz"
check_url "chat frontend" "${CHAT_DOMAIN}" "/"
check_route_status "xmpp websocket route" "${CHAT_DOMAIN}" "/xmpp-websocket"
check_url "meet placeholder" "${MEET_DOMAIN}" "/healthz"
check_admin_denied
check_security_headers

if docker compose --env-file "${ENV_FILE}" exec -T prosody prosodyctl check config >/dev/null; then
	echo "ok: prosody config"
else
	echo "error: prosody config"
	exit 1
fi

if docker compose --env-file "${ENV_FILE}" exec -T prosody sh -c '[ "${XMPP_REGISTRATION_ENABLED}" = "false" ]'; then
	echo "ok: prosody registration disabled"
else
	echo "error: prosody registration disabled"
	exit 1
fi

check_federation_disabled
check_converse_registration_hidden
check_unpublished_port prosody 5222
check_unpublished_port prosody 5269
check_postgres_bind
