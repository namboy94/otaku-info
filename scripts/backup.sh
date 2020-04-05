#!/bin/bash

if [ "$1" == "" ] || [ "$2" == "" ]; then
        echo "Usage: backup.sh <container name> <sql file>"
        exit 1
fi

CONTAINER_NAME="$1"
DATABASE_DUMP="$2"

docker exec -i "$CONTAINER_NAME" bash -c 'pg_dump $POSTGRES_DB -U $POSTGRES_USER' > "$DATABASE_DUMP"