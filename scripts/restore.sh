#!/bin/bash

if [ "$1" == "" ] || [ "$2" == "" ]; then
        echo "Usage: restore.sh <container name> <sql file>"
        exit 1
fi

CONTAINER_NAME="$1"
DATABASE_DUMP="$2"

docker exec -i "$CONTAINER_NAME" bash -c 'dropdb $POSTGRES_DB -U $POSTGRES_USER'
docker exec -i "$CONTAINER_NAME" bash -c 'createdb $POSTGRES_DB -U $POSTGRES_USER'
docker exec -i "$CONTAINER_NAME" bash -c 'psql $POSTGRES_DB -U $POSTGRES_USER' < "$DATABASE_DUMP"
