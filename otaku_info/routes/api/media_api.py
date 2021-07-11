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

from typing import List
from flask.blueprints import Blueprint
from jerrycan.base import db
from jerrycan.routes.decorators import api
from jerrycan.exceptions import ApiException
from otaku_info.Config import Config
from otaku_info.db.MediaItem import MediaItem
from otaku_info.enums import MediaType, ListService


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)
    api_base_path = f"/api/v{Config.API_VERSION}"

    @blueprint.route(
        f"{api_base_path}/media_ids/<service>/<media_type>/<service_id>",
        methods=["GET"]
    )
    @api
    def media_ids(service: str, media_type: str, service_id: str):
        """
        Retrieves all media IDs for a media item
        :return: The IDs for the media item
        """
        media_item: MediaItem = MediaItem.query.filter_by(
            service=ListService(service),
            media_type=MediaType(media_type),
            service_id=service_id
        ).first()
        if media_item is None:
            raise ApiException("ID does not exist", 404)

        return {x.name: y.service_id for x, y in media_item.ids.items()}

    @blueprint.route(f"{api_base_path}/id_mappings")
    def all_id_mappings():
        """
        Dumps all the ID mappings currently stored in the database
        :return: The ID Mappings
        """
        all_items: List[MediaItem] = MediaItem.query.options(
            db.joinedload(MediaItem.id_mappings)
        ).all()

        item_map = {
            x.name: {y.name: {} for y in MediaType}
            for x in ListService
        }
        for media_item in all_items:
            for service, mapping in media_item.ids.items():
                item_map[service.name][media_item.media_type.name] = \
                    mapping.service_id

        return {"mappings": item_map}

    return blueprint
