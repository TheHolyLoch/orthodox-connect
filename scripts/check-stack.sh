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

HTTPS_PORT="${HTTPS_PORT:-8443}"
PORTAL_DOMAIN="${PORTAL_DOMAIN:-portal.orthodox-connect.localhost}"
CHAT_DOMAIN="${CHAT_DOMAIN:-chat.orthodox-connect.localhost}"
MEET_DOMAIN="${MEET_DOMAIN:-meet.orthodox-connect.localhost}"

check_url() {
	local name="$1"
	local host="$2"
	local path="$3"

	if curl -kfsS --resolve "${host}:${HTTPS_PORT}:127.0.0.1" "https://${host}:${HTTPS_PORT}${path}" >/dev/null; then
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

	status="$(curl -k -sS -o /dev/null -w '%{http_code}' --resolve "${host}:${HTTPS_PORT}:127.0.0.1" "https://${host}:${HTTPS_PORT}${path}")"

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

docker compose --env-file "${ENV_FILE}" ps

check_url "portal health" "${PORTAL_DOMAIN}" "/healthz"
check_url "chat frontend" "${CHAT_DOMAIN}" "/"
check_route_status "xmpp websocket route" "${CHAT_DOMAIN}" "/xmpp-websocket"
check_url "meet placeholder" "${MEET_DOMAIN}" "/healthz"
