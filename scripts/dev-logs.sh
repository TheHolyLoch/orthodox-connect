#!/usr/bin/env bash
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/scripts/dev-logs.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [ "$#" -gt 0 ]; then
	docker compose --env-file .env logs -f "$@"
else
	docker compose --env-file .env logs -f
fi
