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

from flask import request, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from puffotter.flask.base import db
from otaku_info.utils.enums import ListService
from otaku_info.db.ServiceUsername import ServiceUsername


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/set_service_username", methods=["POST"])
    @login_required
    def set_service_username():
        """
        Sets an exernal service username for the current user
        :return:
        """
        username = request.form["username"]
        service = ListService(request.form["service"])

        service_username: ServiceUsername = ServiceUsername.query\
            .filter_by(user=current_user, service=service).first()
        if service_username is None:
            service_username = ServiceUsername(
                user=current_user, username=username, service=service
            )
            db.session.add(service_username)
        else:
            service_username.username = username

        db.session.commit()
        return redirect(url_for("user_management.profile"))

    return blueprint
