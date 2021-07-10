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

import time
from typing import List, Optional, Dict
from jerrycan.base import app, db

from otaku_info.db import MediaList, MediaListItem, MediaIdMapping
from otaku_info.enums import ListService, MediaType
from otaku_info.utils.object_conversion import anime_list_item_to_media_item, \
    anilist_user_item_to_media_user_state
from otaku_info.db.ServiceUsername import ServiceUsername
from otaku_info.external.anilist import load_anilist
from otaku_info.external.entities.AnilistUserItem import AnilistUserItem


def update_anilist_data(usernames: Optional[List[ServiceUsername]] = None):
    """
    Retrieves all entries on the anilists of all users that provided
    an anilist username
    :param usernames: Can be used to override the usernames to use
    :return: None
    """
    start = time.time()
    app.logger.info("Starting Anilist Update")

    if usernames is None:
        usernames = ServiceUsername.query\
            .filter_by(service=ListService.ANILIST).all()

    anilist_data: Dict[
        ServiceUsername,
        Dict[MediaType, List[AnilistUserItem]]
    ] = {
        username: {
            media_type: load_anilist(username.username, media_type)
            for media_type in MediaType
        }
        for username in usernames
    }
    __update_data(anilist_data)
    app.logger.info(f"Finished Anilist Update in {time.time() - start}s.")


def __update_data(
        anilist_data: Dict[
            ServiceUsername,
            Dict[MediaType, List[AnilistUserItem]]
        ]
):
    """
    Updates the anilist data in the database
    :param anilist_data: The anilist data to enter
    :return: None
    """
    media_items = {}
    user_states = []
    user_lists = {}
    user_list_items = []
    mal_mappings = []

    for username, anilist_info in anilist_data.items():
        for media_type, anilist_items in anilist_info.items():
            for anilist_item in anilist_items:
                media_item = anime_list_item_to_media_item(anilist_item)
                user_state = anilist_user_item_to_media_user_state(
                    anilist_item, username.user_id
                )
                media_list = MediaList(
                    service=ListService.ANILIST,
                    media_type=anilist_item.media_type,
                    user_id=username.user_id,
                    name=anilist_item.list_name
                )
                media_list_item = MediaListItem(
                    media_list_service=media_list.service,
                    media_list_media_type=media_list.media_type,
                    media_list_user_id=media_list.user_id,
                    media_list_name=media_list.name,
                    user_state_service=user_state.service,
                    user_state_media_type=user_state.media_type,
                    user_state_user_id=user_state.user_id,
                    user_state_service_id=user_state.service_id
                )
                media_item_tuple = (
                    media_item.service,
                    media_item.service_id,
                    media_item.media_type
                )
                media_list_tuple = (
                    media_list.service,
                    media_list.media_type,
                    media_list.user_id,
                    media_list.name
                )
                media_items[media_item_tuple] = media_item
                user_states.append(user_state)
                user_lists[media_list_tuple] = media_list
                user_list_items.append(media_list_item)
                if anilist_item.myanimelist_id is not None:
                    mal_mapping = MediaIdMapping(
                        service=ListService.MYANIMELIST,
                        service_id=str(anilist_item.myanimelist_id),
                        parent_service=ListService.ANILIST,
                        parent_service_id=media_item.service_id,
                        media_type=media_item.media_type
                    )
                    mal_mappings.append(mal_mapping)

    for media_item in media_items.values():
        app.logger.debug(f"Upserting anilist item {media_item.title}")
        db.session.merge(media_item)
    for user_state in user_states:
        db.session.merge(user_state)
    for media_list in user_lists.values():
        db.session.merge(media_list)
    for media_list_item in user_list_items:
        db.session.merge(media_list_item)
    for mal_mapping in mal_mappings:
        db.session.merge(mal_mapping)
        app.logger.debug(f"Upserting id mapping: "
                         f"anilist:{mal_mapping.parent_service_id} "
                         f"-> myanimelist:{mal_mapping.service_id}")
    db.session.commit()
