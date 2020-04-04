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

from flask import request, render_template, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from puffotter.flask.base import app
from otaku_info_web.utils.enums import MediaType
from otaku_info_web.utils.manga_updates.generator import prepare_manga_updates
from otaku_info_web.db.MediaList import MediaList


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/manga/updates", methods=["GET", "POST"])
    @login_required
    def show_manga_updates():
        """
        Shows the user's manga updates for a specified service and list
        :return: The response
        """
        app.logger.debug("manga/updates request start")
        if request.method == "POST":
            args = request.form
            service, list_name = args["list_ident"].split(":", 1)
        else:
            args = request.args
            service = args.get("service")
            list_name = args.get("list_name")

        only_updates = args.get("only_updates", "off") == "on"
        include_complete = args.get("include_complete", "off") == "on"

        if request.method == "POST":
            url = f"{url_for('manga.show_manga_updates')}" \
                  f"?service={service}" \
                  f"&list_name={list_name}" \
                  f"&only_updates={'on' if only_updates else 'off'}" \
                  f"&include_complete={'on' if include_complete else 'off'}"
            return redirect(url)

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
                    service,
                    list_name,
                    include_complete,
                    only_updates
                )
            return render_template(
                "manga/manga_updates.html",
                entries=list_entries,
                list_name=list_name,
                service=service
            )

    return blueprint
