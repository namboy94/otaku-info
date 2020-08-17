"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info.

otaku-info is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from datetime import datetime
from flask import request, render_template, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from otaku_info.utils.enums import MediaType, ListService
from otaku_info.utils.manga_updates.generator import prepare_manga_updates
from otaku_info.db.MediaList import MediaList
from otaku_info.utils.reddit.ln_releases import load_ln_releases


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/ln/releases", methods=["GET"])
    def ln_releases():
        """
        Displays light novel releases
        :return: The response
        """
        year = request.args.get("year")
        month = request.args.get("month", datetime.utcnow().month)
        releases = load_ln_releases(year, month)
        return render_template(
            "ln/ln_releases.html",
            releases=releases
        )

    return blueprint
