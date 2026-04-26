#!/usr/bin/env bash
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/scripts/backup.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

[ -f .env ] && source .env || { echo "error: missing .env file" && exit 1; }

BACKUP_ROOT="${BACKUP_ROOT:-./backups}"
BACKUP_TIMESTAMP="$(date -u +'%Y%m%dT%H%M%SZ')"
BACKUP_DIR="${BACKUP_ROOT%/}/${BACKUP_TIMESTAMP}"

require_command() {
	command -v "$1" >/dev/null 2>&1 || { echo "error: missing required command: $1" && exit 1; }
}

compose() {
	docker compose --env-file .env "$@"
}

backup_volume() {
	local volume_name="$1"
	local output_name="$2"

	if ! docker volume inspect "${volume_name}" >/dev/null 2>&1; then
		echo "skip: volume ${volume_name} does not exist"

		return
	fi

	docker run --rm \
		-v "${volume_name}:/source:ro" \
		-v "${BACKUP_DIR}/volumes:/backup" \
		alpine:3.20 \
		tar -C /source -czf "/backup/${output_name}.tar.gz" .
}

copy_if_present() {
	local source_path="$1"
	local output_path="$2"

	if [ -e "${source_path}" ]; then
		mkdir -p "$(dirname "${BACKUP_DIR}/${output_path}")"
		cp -a "${source_path}" "${BACKUP_DIR}/${output_path}"
	fi
}

write_manifest() {
	{
		echo "created_at=${BACKUP_TIMESTAMP}"
		echo "root_domain=${ROOT_DOMAIN:-}"
		echo "postgres_db=${POSTGRES_DB:-}"
		echo "backup_format=orthodox-connect-local-v1"
	} > "${BACKUP_DIR}/manifest.txt"
}

main() {
	require_command docker
	require_command cp
	require_command date
	require_command mkdir
	require_command tar

	mkdir -p "${BACKUP_DIR}/postgres" "${BACKUP_DIR}/files" "${BACKUP_DIR}/volumes"

	compose exec -T postgres pg_dump \
		-U "${POSTGRES_USER}" \
		-d "${POSTGRES_DB}" \
		--clean \
		--if-exists \
		--no-owner \
		--no-privileges \
		> "${BACKUP_DIR}/postgres/${POSTGRES_DB}.sql"

	copy_if_present prosody "files/prosody"
	copy_if_present jitsi "files/jitsi"
	copy_if_present reverse-proxy "files/reverse-proxy"
	copy_if_present portal/migrations "files/portal/migrations"

	backup_volume "${COMPOSE_PROJECT_NAME:-orthodox-connect}_prosody_data" "prosody_data"
	backup_volume "${COMPOSE_PROJECT_NAME:-orthodox-connect}_jitsi_web_config" "jitsi_web_config"
	backup_volume "${COMPOSE_PROJECT_NAME:-orthodox-connect}_jitsi_prosody_config" "jitsi_prosody_config"
	backup_volume "${COMPOSE_PROJECT_NAME:-orthodox-connect}_jitsi_jicofo_config" "jitsi_jicofo_config"
	backup_volume "${COMPOSE_PROJECT_NAME:-orthodox-connect}_jitsi_jvb_config" "jitsi_jvb_config"
	backup_volume "${COMPOSE_PROJECT_NAME:-orthodox-connect}_reverse_proxy_data" "reverse_proxy_data"
	backup_volume "${COMPOSE_PROJECT_NAME:-orthodox-connect}_reverse_proxy_config" "reverse_proxy_config"

	write_manifest

	echo "${BACKUP_DIR}"
}

main "$@"
