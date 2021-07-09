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
from jerrycan.routes.decorators import api
from jerrycan.exceptions import ApiException
from otaku_info.Config import Config
from otaku_info.db.MediaIdMapping import MediaId
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
        f"{api_base_path}/media_ids/<_service>/<_media_type>/<service_id>",
        methods=["GET"]
    )
    @api
    def media_ids(_service: str, _media_type: str, service_id: str):
        """
        Retrieves all media IDs for a media ID
        :return: The response
        """
        service = ListService(_service)
        media_type = MediaType(_media_type)

        matching_ids: List[MediaItem] = [
            x for x in
            MediaId.query
            .filter_by(service_id=service_id, service=service).all()
            if x.media_item.media_type == media_type
        ]

        if len(matching_ids) < 1:
            raise ApiException("ID does not exist", 404)

        media_item = matching_ids[0].media_item

        id_mappings = {
            x.service.value: x.service_id
            for x in MediaId.query.filter_by(media_item_id=media_item.id).all()
        }
        id_mappings["otaku_info"] = str(media_item.id)

        return id_mappings

    @blueprint.route(f"{api_base_path}/id_mappings")
    def all_id_mappings():
        """
        Dumps all the ID mappings currently stored in the database
        :return: None
        """
        all_ids: List[MediaId] = MediaId.query.all()

        item_map = {}
        for media_id in all_ids:
            if media_id.media_item_id not in item_map:
                item_map[media_id.media_item_id] = {}
            item_map[media_id.media_item_id][media_id.service.name] = \
                media_id.service_id

        return {"mappings": list(item_map.values())}

    return blueprint
