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
from otaku_info_web.routes.static import static_blueprint
from otaku_info_web.routes.manga import manga_blueprint
from otaku_info_web.routes.user_management import user_management_blueprint
from otaku_info_web.routes.api.user_management import \
    user_management_api_blueprint


def register_blueprints(app: Flask):
    """
    Registers all route blueprints in the flask app
    :param app: The flask application
    :return: None
    """
    for blueprint in [
        static_blueprint,
        user_management_blueprint,
        user_management_api_blueprint,
        manga_blueprint
    ]:
        app.register_blueprint(blueprint)
