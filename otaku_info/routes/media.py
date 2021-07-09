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
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaIdMapping import MediaIdMapping


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/media/<media_item_id>", methods=["GET"])
    def media(media_item_id: int):
        """
        Displays information on a media item
        :param media_item_id: The ID of the media item
        :return: None
        """
        media_item: MediaItem = MediaItem.query\
            .options(db.joinedload(MediaItem.media_ids)
                     .subqueryload(MediaIdMapping.media_user_states)
                     ).filter_by(id=media_item_id).first()

        if media_item is None:
            abort(404)

        if current_user is not None:
            media_user_states = []
            for media_id in media_item.media_ids:
                user_states = [
                    x for x in media_id.media_user_states
                    if x.user_id == current_user.id
                ]
                media_user_states += user_states
            media_user_states.sort(key=lambda x: x.media_id.service.value)
        else:
            media_user_states = []

        return render_template(
            "media/media.html",
            media_item=media_item,
            media_user_states=media_user_states
        )

    return blueprint
