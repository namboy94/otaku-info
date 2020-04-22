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

from flask import request
from flask.blueprints import Blueprint
from puffotter.flask.routes.decorators import api
from otaku_info_web.Config import Config
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.entities.Address import Address


def define_blueprint(blueprint_name: str) -> Blueprint:
    blueprint = Blueprint(blueprint_name, __name__)
    api_base_path = f"/api/v{Config.API_VERSION}"

    @blueprint.route(f"{api_base_path}/telegram", methods=["GET"])
    @api
    def telegram_test():
        telegram = Config.TELEGRAM_BOT_CONNECTION
        telegram.send(TextMessage(
            telegram.address,
            Address(request.args["chat"]),
            "Hello"
        ))
    return blueprint
