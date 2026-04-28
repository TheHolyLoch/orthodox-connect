#!/usr/bin/env bash
# Orthodox Connect - Developed by dgm (dgm@tuta.com)
# orthodox-connect/scripts/dev-up.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [ ! -f .env ]; then
	cp .env.example .env
fi

docker compose --env-file .env up -d --build
