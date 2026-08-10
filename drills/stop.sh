#!/bin/sh
set -e
cd "$(dirname "$0")"
docker compose down > /dev/null 2>&1 || true
echo "止めた。(work/ のノートブックは残してある)"
