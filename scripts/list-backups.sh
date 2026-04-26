#!/usr/bin/env bash
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/scripts/list-backups.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

[ -f .env ] && source .env || { echo "error: missing .env file" && exit 1; }

BACKUP_ROOT="${BACKUP_ROOT:-./backups}"

if [ ! -d "${BACKUP_ROOT}" ]; then
	echo "no backups found"

	exit 0
fi

find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d | sort
