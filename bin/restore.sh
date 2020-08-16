#!/bin/bash
# Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>
#
# This file is part of otaku-info.
#
# otaku-info is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# otaku-info is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with otaku-info.  If not, see <http://www.gnu.org/licenses/>.

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: restore.sh <backup-file>"
fi

APP="otaku-info-app"
DB="otaku-info-db"
TARGET=$1

rm -rf backup .env
tar xvf "$TARGET"
cp backup/.env .env
docker-compose down
docker-compose up -d
docker stop "$APP"
sleep 20

docker exec -i "$DB" bash -c 'mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -e "DROP DATABASE $MYSQL_DATABASE; CREATE DATABASE $MYSQL_DATABASE"'
docker exec -i "$DB" bash -c 'mysql -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE' < backup/db.sql
docker-compose up -d
rm -rf backup
