#!/bin/bash

if [ "$1" == "" ]; then
        echo "Please enter docker container name"
        exit 1
fi
if [ "$2" == "" ]; then
        echo "Please specify database dump"
        exit 1
fi


CONTAINER_NAME="$1"
DATABASE_DUMP="$2"

echo 1
docker exec -i "$CONTAINER_NAME" bash -c 'mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e "DROP DATABASE $MYSQL_DATABASE; CREATE DATABASE $MYSQL_DATABASE"'
echo 2
docker exec -i "$CONTAINER_NAME" bash -c 'mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE' < "$DATABASE_DUMP"
echo 3