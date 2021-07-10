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
from flask_login import current_user
from jerrycan.base import db

from otaku_info.db import MediaUserState
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaIdMapping import MediaIdMapping
from otaku_info.enums import ListService, MediaType


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route(
        f"/media/<service>/<media_type>/<service_id>",
        methods=["GET"]
    )
    def media(service: str, media_type: str, service_id: str):
        """
        Displays information on a media item
        :param service: The service of the media item
        :param media_type: The media type of the item
        :param service_id: The service ID of the item
        :return: The page displaying information on the media item
        """
        media_item: MediaItem = MediaItem.query.filter_by(
            service=ListService(service),
            media_type=MediaType(media_type),
            service_id=service_id
        ).first()
        if media_item is None:
            abort(404)

        user_state = None
        if current_user.is_authenticated:
            user_state = MediaUserState.query.filter_by(
                service=ListService(service),
                media_type=MediaType(media_type),
                service_id=service_id,
                user_id=current_user.id
            ).first()

        return render_template(
            "media/media.html",
            media_item=media_item,
            user_state=user_state
        )

    return blueprint
