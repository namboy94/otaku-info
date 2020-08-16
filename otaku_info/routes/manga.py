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

from flask import request, render_template, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from otaku_info.utils.enums import MediaType, ListService
from otaku_info.utils.manga_updates.generator import prepare_manga_updates
from otaku_info.db.MediaList import MediaList


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/manga/updates", methods=["POST"])
    @login_required
    def redirect_manga_updates():
        """
        Redirects a POST requests to the appropriate GET request for
        the /manga/updates route
        :return: The response
        """
        service, list_name = request.form["list_ident"].split(":", 1)
        mincount = request.form.get("mincount", "0")
        include_complete = request.form.get("include_complete", "off") == "on"

        get_url = url_for("manga.show_manga_updates")
        get_url += f"?service={service}" \
                   f"&list_name={list_name}" \
                   f"&mincount={mincount}" \
                   f"&include_complete={1 if include_complete else 0}"

        return redirect(get_url)

    @blueprint.route("/manga/updates", methods=["GET"])
    @login_required
    def show_manga_updates():
        """
        Shows the user's manga updates for a specified service and list
        :return: The response
        """
        service = request.args.get("service")
        list_name = request.args.get("list_name")
        mincount = int(request.args.get("mincount", "0"))
        include_complete = request.args.get("include_complete", "0") == "1"

        if service is None or list_name is None:
            media_lists = [
                x for x in MediaList.query.filter_by(
                    user=current_user, media_type=MediaType.MANGA
                )
            ]
            return render_template(
                "manga/manga_updates.html",
                media_lists=media_lists
            )
        else:
            list_entries = \
                prepare_manga_updates(
                    current_user,
                    ListService(service),
                    list_name,
                    include_complete,
                    mincount
                )
            list_entries.sort(key=lambda x: x.score, reverse=True)
            return render_template(
                "manga/manga_updates.html",
                entries=list_entries,
                list_name=list_name,
                service=service
            )

    return blueprint
