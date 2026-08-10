#!/bin/sh
set -e
cd "$(dirname "$0")"
docker compose down -v > /dev/null 2>&1 || true
rm -rf data out .env
echo "cleaned up. (work/ の自分のコードは残してある。git管理外なのでコミットされない)"
