#!/bin/bash
set -e

# Prüfe, ob der Datenbankordner leer ist (was bei einem neuen Volume der Fall wäre)
if [ -z "$(ls -A /app/database)" ]; then
  echo "copying database"
  cp -r /app/database_init/* /app/database/
fi

# Starte die Hauptanwendung
exec "$@"