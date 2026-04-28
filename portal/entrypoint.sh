#!/usr/bin/env bash
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/portal/entrypoint.sh

set -euo pipefail

attempt=1
max_attempts="${PORTAL_DB_MIGRATION_ATTEMPTS:-30}"

while [ "${attempt}" -le "${max_attempts}" ]; do
	if python3 -m portal.app.cli migrate; then
		break
	fi

	echo "portal: waiting for postgres (${attempt}/${max_attempts})"
	attempt=$((attempt + 1))
	sleep 2
done

if [ "${attempt}" -gt "${max_attempts}" ]; then
	echo "portal: database migration did not complete"
	exit 1
fi

exec python3 -m portal.app.admin
