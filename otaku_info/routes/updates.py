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

from flask import request, render_template, redirect, url_for, flash
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from otaku_info.enums import ListService, MediaType, MediaSubType
from otaku_info.db.MediaList import MediaList
from otaku_info.wrappers.UpdateWrapper import UpdateWrapper


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/updates", methods=["POST"])
    @login_required
    def redirect_updates():
        """
        Redirects a POST requests to the appropriate GET request for
        the /updates route
        :return: The response
        """
        service, media_type, list_name = \
            request.form["list_ident"].split(":", 2)
        mincount = request.form.get("mincount", "0")
        include_complete = request.form.get("include_complete", "off") == "on"
        filter_subtype = request.form.get("filter_subtype")

        get_url = url_for(
            "updates.show_updates",
            service=service,
            media_type=media_type,
            list_name=list_name,
            mincount=mincount,
            include_complete=1 if include_complete else 0,
            filter_subtype=filter_subtype
        )
        return redirect(get_url)

    @blueprint.route("/updates", methods=["GET"])
    @login_required
    def show_updates():
        """
        Shows the user's manga updates for a specified service and list
        :return: The response
        """
        service_name = request.args.get("service")
        media_type_name = request.args.get("media_type")
        list_name = request.args.get("list_name")
        mincount = int(request.args.get("mincount", "0"))
        include_complete = request.args.get("include_complete", "0") == "1"
        subtype_name = request.args.get("filter_subtype")

        if service_name is None \
                or list_name is None \
                or media_type_name is None:
            media_lists = [
                x for x in MediaList.query.filter_by(user=current_user)
            ]
            media_lists.sort(key=lambda x: x.name)
            media_lists.sort(key=lambda x: x.media_type.value)
            media_lists.sort(key=lambda x: x.service.value)
            return render_template(
                "updates/updates.html",
                media_lists=[
                    (
                        f"{x.service.value}:{x.media_type.value}:{x.name}",
                        f"{x.service.value.title()}:"
                        f"{x.media_type.value.title()}:{x.name.title()}"

                    )
                    for x in media_lists
                ],
                subtypes=[(x.value, x.value.title()) for x in MediaSubType]
            )
        else:
            try:
                service = ListService(service_name)
                media_type = MediaType(media_type_name)
                if subtype_name is None or subtype_name == "":
                    subtype = None
                else:
                    subtype = MediaSubType(subtype_name)
            except ValueError:
                flash("Invalid configuration", "danger")
                return redirect(url_for("updates.show_updates"))

            updates = UpdateWrapper.from_db(
                current_user,
                list_name,
                service,
                media_type,
                subtype,
                mincount,
                include_complete
            )
            return render_template(
                "updates/updates.html",
                updates=updates,
                list_name=list_name,
                service=service,
                media_type=media_type
            )

    return blueprint
