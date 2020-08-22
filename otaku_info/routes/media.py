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

from flask import render_template, abort
from flask.blueprints import Blueprint
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaId import MediaId


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/media/<media_item_id>", methods=["GET"])
    def media(media_item_id: int):
        media_item = MediaItem.query.get(media_item_id)

        if media_item is None:
            abort(404)

        media_ids = MediaId.query.filter_by(media_item_id=media_item_id).all()
        return render_template(
            "media/media.html",
            media_item=media_item,
            media_ids=media_ids
        )

    @blueprint.route("/test")
    def test():
        from otaku_info.db.ServiceUsername import ServiceUsername
        from otaku_info.background.anilist import update_anilist_data
        update_anilist_data(ServiceUsername.query.all())
        return "OK"

    @blueprint.route("/setup")
    def testsetup():
        from puffotter.flask.base import db
        from puffotter.flask.db.User import User
        from otaku_info.db.ServiceUsername import ServiceUsername
        from otaku_info.enums import ListService
        user = User(id=100, username="test", email="test@example.com",
                    confirmed=True, confirmation_hash="", password_hash="")
        username = ServiceUsername(user=user, username="namboy94",
                                   service=ListService.ANILIST)
        db.session.add(user)
        db.session.add(username)
        db.session.commit()
        return "OK"

    return blueprint
