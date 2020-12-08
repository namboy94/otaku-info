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
from jerrycan.base import app
from otaku_info.utils.db.DbQueue import DbQueue
from otaku_info.db.ServiceUsername import ServiceUsername
from otaku_info.external.anilist import load_anilist
from otaku_info.external.entities.AnilistUserItem import AnilistUserItem
from otaku_info.enums import ListService, MediaType


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

    for username, anilist_info in anilist_data.items():
        for media_type, anilist_items in anilist_info.items():
            for anilist_item in anilist_items:
                __perform_update(
                    anilist_item,
                    username
                )

    app.logger.info(f"Finished Anilist Update in {time.time() - start}s.")


def __perform_update(
        anilist_item: AnilistUserItem,
        username: ServiceUsername
):
    """
    Inserts or updates the contents of a single anilist user item
    :param anilist_item: The anilist user item
    :param username: The service username
    :return: None
    """
    media_item_params = {
        "media_type": anilist_item.media_type,
        "media_subtype": anilist_item.media_subtype,
        "english_title": anilist_item.english_title,
        "romaji_title": anilist_item.romaji_title,
        "cover_url": anilist_item.cover_url,
        "latest_release": anilist_item.latest_release,
        "latest_volume_release": anilist_item.volumes,
        "releasing_state": anilist_item.releasing_state,
        "next_episode": anilist_item.next_episode,
        "next_episode_airing_time": anilist_item.next_episode_airing_time
    }
    service_ids = {
        ListService.ANILIST: str(anilist_item.id)
    }
    if anilist_item.myanimelist_id is not None:
        service_ids[ListService.MYANIMELIST] = str(anilist_item.myanimelist_id)
    user_state_params = {
        "user_id": username.user_id,
        "progress": anilist_item.progress,
        "volume_progress": anilist_item.volume_progress,
        "score": anilist_item.score,
        "consuming_state": anilist_item.consuming_state
    }
    media_list_params = {
        "user_id": username.user_id,
        "name": anilist_item.list_name,
        "service": ListService.ANILIST,
        "media_type": anilist_item.media_type
    }
    DbQueue.queue_media_item(
        media_item_params,
        ListService.ANILIST,
        service_ids,
        user_state_params,
        media_list_params
    )
