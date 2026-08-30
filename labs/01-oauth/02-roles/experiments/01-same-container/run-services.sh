#!/bin/bash

set -e

fastapi run /code/authorization-server/app/main.py --host 0.0.0.0 --port 9000 &
AUTH_PID=$!

fastapi run /code/resource-server/app/main.py --host 0.0.0.0 --port 8000 &
RESOURCE_PID=$!

trap 'kill "$AUTH_PID" "$RESOURCE_PID" 2>/dev/null || true' SIGTERM SIGINT

wait -n "$AUTH_PID" "$RESOURCE_PID"
STATUS=$?

kill "$AUTH_PID" "$RESOURCE_PID" 2>/dev/null || true

wait "$AUTH_PID" "$RESOURCE_PID" 2>/dev/null || true

exit "$STATUS"