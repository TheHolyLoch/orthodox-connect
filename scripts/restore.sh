#!/usr/bin/env bash
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/scripts/restore.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

[ -f .env ] && source .env || { echo "error: missing .env file" && exit 1; }

BACKUP_ROOT="${BACKUP_ROOT:-./backups}"
BACKUP_NAME="${1:-}"
BACKUP_DIR="${BACKUP_NAME}"
COMPOSE_PROJECT="${COMPOSE_PROJECT_NAME:-orthodox_connect}"
RESTORE_MODE="${2:-}"

require_command() {
	command -v "$1" >/dev/null 2>&1 || { echo "error: missing required command: $1" && exit 1; }
}

compose() {
	docker compose --env-file .env "$@"
}

resolve_backup_dir() {
	if [ -z "${BACKUP_NAME}" ]; then
		echo "usage: scripts/restore.sh <backup-directory-or-name>"
		exit 1
	fi

	if [ ! -d "${BACKUP_DIR}" ]; then
		BACKUP_DIR="${BACKUP_ROOT%/}/${BACKUP_NAME}"
	fi

	[ -d "${BACKUP_DIR}" ] || { echo "error: backup not found: ${BACKUP_NAME}" && exit 1; }
	[ -f "${BACKUP_DIR}/manifest.txt" ] || { echo "error: missing backup manifest" && exit 1; }
	[ -f "${BACKUP_DIR}/postgres/${POSTGRES_DB}.sql" ] || { echo "error: missing PostgreSQL dump" && exit 1; }
}

restore_volume() {
	local volume_name="$1"
	local input_name="$2"
	local archive_path="${BACKUP_DIR}/volumes/${input_name}.tar.gz"

	if [ ! -f "${archive_path}" ]; then
		echo "skip: backup archive ${input_name}.tar.gz not found"

		return
	fi

	docker volume inspect "${volume_name}" >/dev/null 2>&1 || docker volume create "${volume_name}" >/dev/null
	docker run --rm \
		-v "${volume_name}:/target" \
		-v "${BACKUP_DIR}/volumes:/backup:ro" \
		alpine:3.20 \
		sh -c "find /target -mindepth 1 -maxdepth 1 -exec rm -rf {} + && tar -C /target -xzf /backup/${input_name}.tar.gz"
}

restore_postgres() {
	compose up -d postgres
	compose exec -T postgres psql \
		-U "${POSTGRES_USER}" \
		-d "${POSTGRES_DB}" \
		-v ON_ERROR_STOP=1 \
		< "${BACKUP_DIR}/postgres/${POSTGRES_DB}.sql"
}

service_exists() {
	local service_name="$1"

	compose config --services | grep -qx "${service_name}"
}

stop_if_present() {
	local service_name="$1"

	if service_exists "${service_name}"; then
		compose stop "${service_name}"
	else
		echo "skip: service ${service_name} is not defined"
	fi
}

validate_backup() {
	echo "backup=${BACKUP_DIR}"
	echo "manifest=ok"
	echo "postgres_dump=${BACKUP_DIR}/postgres/${POSTGRES_DB}.sql"

	for archive_name in \
		prosody_data \
		jitsi_web_config \
		jitsi_prosody_config \
		jitsi_jicofo_config \
		jitsi_jvb_config \
		reverse_proxy_data \
		reverse_proxy_config
	do
		if [ -f "${BACKUP_DIR}/volumes/${archive_name}.tar.gz" ]; then
			echo "volume_archive=${archive_name}:ok"
		else
			echo "volume_archive=${archive_name}:missing"
		fi
	done
}

main() {
	require_command docker
	require_command find
	require_command grep
	require_command tar

	resolve_backup_dir

	if [ "${RESTORE_MODE}" = "--dry-run" ] || [ "${RESTORE_DRY_RUN:-}" = "true" ]; then
		validate_backup

		return
	fi

	if [ "${RESTORE_CONFIRM:-}" != "restore-local-backup" ]; then
		echo "error: set RESTORE_CONFIRM=restore-local-backup before restoring"
		exit 1
	fi

	echo "warning: restore will overwrite PostgreSQL data and supported service volumes"

	for service_name in portal converse prosody jitsi-web jitsi-prosody jitsi-jicofo jitsi-jvb reverse-proxy
	do
		stop_if_present "${service_name}"
	done

	restore_postgres
	restore_volume "${COMPOSE_PROJECT}_prosody_data" "prosody_data"
	restore_volume "${COMPOSE_PROJECT}_jitsi_web_config" "jitsi_web_config"
	restore_volume "${COMPOSE_PROJECT}_jitsi_prosody_config" "jitsi_prosody_config"
	restore_volume "${COMPOSE_PROJECT}_jitsi_jicofo_config" "jitsi_jicofo_config"
	restore_volume "${COMPOSE_PROJECT}_jitsi_jvb_config" "jitsi_jvb_config"
	restore_volume "${COMPOSE_PROJECT}_reverse_proxy_data" "reverse_proxy_data"
	restore_volume "${COMPOSE_PROJECT}_reverse_proxy_config" "reverse_proxy_config"

	echo "restore complete: ${BACKUP_DIR}"
}

main "$@"
