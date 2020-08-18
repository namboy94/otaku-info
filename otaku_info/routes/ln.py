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
from flask import request, render_template
from flask.blueprints import Blueprint
from otaku_info.db.LnRelease import LnRelease


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
        try:
            year = int(request.args.get("year"))
        except (TypeError, ValueError):
            year = None
        try:
            month = int(request.args.get("month"))
        except (TypeError, ValueError):
            month = None

        now = datetime.utcnow()
        if not (year is not None and month is None):
            if year is None:
                year = now.year
            if month is None:
                month = now.month

        releases = [
            x for x in
            LnRelease.query.all()
            if x.release_date.year == year
        ]
        if month is not None:
            releases = [x for x in releases if x.release_date.month == month]
        releases.sort(key=lambda x: x.release_date)

        return render_template(
            "ln/ln_releases.html",
            releases=releases
        )

    return blueprint
