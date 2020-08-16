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
    echo "Usage: backup.sh <backup-file>"
fi

APP="otaku-info-app"
DB="otaku-info-db"
TARGET=$1

rm -rf backup
mkdir backup

docker-compose up --no-recreate -d
docker exec "$APP" printenv > backup/.env
docker exec "$DB" bash -c 'mysqldump --single-transaction \
    -h localhost -u $MYSQL_USER --password=$MYSQL_PASSWORD $MYSQL_DATABASE' \
     > backup/db.sql
tar -zcvpf "$TARGET" backup
rm -rf backup
