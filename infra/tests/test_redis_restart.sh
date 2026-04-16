#!/usr/bin/env bash
# Manual verification: Redis AOF persistence survives container restart.
# Run from repository root: bash infra/tests/test_redis_restart.sh
#
# Requires: docker compose up redis -d

set -euo pipefail

echo "1. Writing test data to Redis..."
docker compose exec redis redis-cli LPUSH persistence_test '{"task":"survive","id":"1"}'
docker compose exec redis redis-cli LPUSH persistence_test '{"task":"survive","id":"2"}'
BEFORE=$(docker compose exec redis redis-cli LLEN persistence_test)
echo "   Items before restart: $BEFORE"

echo "2. Restarting Redis container..."
docker compose restart redis
sleep 3

echo "3. Verifying data after restart..."
AFTER=$(docker compose exec redis redis-cli LLEN persistence_test)
echo "   Items after restart: $AFTER"

echo "4. Cleanup..."
docker compose exec redis redis-cli DEL persistence_test

if [ "$BEFORE" = "$AFTER" ]; then
    echo "PASS: All $AFTER items survived Redis restart"
else
    echo "FAIL: Had $BEFORE items, now have $AFTER"
    exit 1
fi
