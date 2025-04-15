#!/bin/bash
set -e

if [ -z "$(ls -A /app/database)" ]; then
  cp -r /app/database_init/* /app/database/
fi

exec "$@"