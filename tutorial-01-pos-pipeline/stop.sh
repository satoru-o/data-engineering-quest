#!/bin/sh
# JupyterLab を止める。
set -e
cd "$(dirname "$0")"
docker compose down > /dev/null 2>&1
echo "止めた。(work/ のノートブックは残してある)"
