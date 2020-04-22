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
from flask_login import login_required, current_user
from puffotter.flask.routes.decorators import api, api_login_required
from otaku_info_web.Config import Config
from otaku_info_web.utils.enums import ListService
from otaku_info_web.utils.manga_updates.generator import prepare_manga_updates


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)
    api_base_path = f"/api/v{Config.API_VERSION}"

    @blueprint.route(f"{api_base_path}/manga_updates", methods=["GET"])
    @api_login_required
    @login_required
    @api
    def fetch_manga_updates():
        """
        :return: The response
        """
        service = request.args.get("service")
        list_name = request.args.get("list_name")
        mincount = int(request.args.get("mincount", "0"))
        include_complete = request.args.get("include_complete", "0") == "1"

        list_entries = prepare_manga_updates(
            current_user,
            ListService(service),
            list_name,
            include_complete,
            mincount
        )
        list_entries.sort(key=lambda x: x.score, reverse=True)
        return [x.__json__() for x in list_entries]

    return blueprint
