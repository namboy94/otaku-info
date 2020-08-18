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
from otaku_info.db.LnRelease import LnRelease
from otaku_info.utils.dates import MONTHS, map_month_name_to_month_number, \
    map_month_number_to_month_name


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
            month = int(request.args["month"])
        except KeyError:
            month = None
        except (TypeError, ValueError):
            month_string = request.args["month"]
            if month_string.lower() == "all":
                month = None
            else:
                month = map_month_name_to_month_number(month_string)

        now = datetime.utcnow()
        if not (year is not None and month is None):
            if year is None:
                year = now.year
            if month is None:
                month = now.month

        all_releases = LnRelease.query.all()
        years = list(set([x.release_date.year for x in all_releases]))
        years.sort()

        releases = [
            x for x in all_releases
            if x.release_date.year == year
        ]
        if month is not None:
            releases = [x for x in releases if x.release_date.month == month]
        releases.sort(key=lambda x: x.release_date)

        if month is None:
            month_name = "all"
        else:
            month_name = map_month_number_to_month_name(month)

        return render_template(
            "ln/ln_releases.html",
            releases=releases,
            years=years,
            months=MONTHS + ["all"],
            selected_year=year,
            selected_month=month_name
        )

    @blueprint.route("/ln/releases", methods=["POST"])
    def ln_releases_form():
        """
        Handles form requests and forwards it to the appropriate GET URL.
        """
        year = request.form.get("year")
        month = request.form.get("month")
        get_url = url_for("ln.ln_releases") + f"?year={year}&month={month}"
        return redirect(get_url)

    return blueprint

