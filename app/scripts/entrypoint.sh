#!/bin/bash
set -e

if [ -z "$(ls -A /app/database)" ]; then
  echo "copying database"
  cp -r /app/database_init/* /app/database/
fi

exec "$@"