"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-web.

otaku-info-web is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-web is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-web.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_tables(app: Flask, db: SQLAlchemy):
    """
    Creates all tables in the database if they don't exist yet
    :param app: The flask application
    :param db: The database
    :return: None
    """
    # noinspection PyUnresolvedReferences
    from otaku_info_web.db.User import User
    # noinspection PyUnresolvedReferences
    from otaku_info_web.db.ApiKey import ApiKey
    # noinspection PyUnresolvedReferences
    from otaku_info_web.db.ExternalUsername import ExternalUsername

    with app.app_context():
        db.create_all()
