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
from typing import List, Optional, cast, Dict, Tuple
from puffotter.flask.base import db, app
from otaku_info.db.MediaId import MediaId
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaListItem import MediaListItem
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.ServiceUsername import ServiceUsername
from otaku_info.external.anilist import load_anilist
from otaku_info.external.entities.AnilistUserItem import AnilistUserItem
from otaku_info.enums import ListService, MediaType
from otaku_info.utils.db.updater import update_or_insert_item
from otaku_info.utils.db.convert import anime_list_item_to_media_id, \
    anime_list_item_to_media_item, anilist_user_item_to_media_user_state, \
    anilist_user_item_to_media_list
from otaku_info.utils.db.load import load_existing_media_data, \
    load_existing_media_list_data


def update_anilist_data(usernames: Optional[List[ServiceUsername]]):
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
    media_items, media_ids, media_user_states = load_existing_media_data()
    media_lists, media_list_items = load_existing_media_list_data()

    for username, anilist_info in anilist_data.items():
        for media_type, anilist_items in anilist_info.items():
            for anilist_item in anilist_items:
                __perform_update(
                    anilist_item,
                    username,
                    media_items,
                    media_ids,
                    media_user_states,
                    media_lists,
                    media_list_items
                )

    db.session.commit()  # Commit pending Updates
    app.logger.info(f"Finished Anilist Update in {time.time() - start}s.")


def __perform_update(
        anilist_item: AnilistUserItem,
        username: ServiceUsername,
        media_items: Dict[Tuple, MediaItem],
        media_ids: Dict[Tuple, MediaId],
        media_user_states: Dict[Tuple, MediaUserState],
        media_lists: Dict[Tuple, MediaList],
        media_list_items: Dict[Tuple, MediaListItem]
):
    """
    Inserts or updates the contents of a single anilist user item
    :param anilist_item: The anilist user item
    :param username: The service username
    :param media_items: Existing media items
    :param media_ids: Existing media ids
    :param media_user_states: Existing media user states
    :param media_lists: Existing media lists
    :param media_list_items: Existing media list items
    :param myanimelist_ids: Existing myanimelist IDs
    :return: None
    """
    media_item = anime_list_item_to_media_item(anilist_item)
    media_item = cast(MediaItem, update_or_insert_item(
        media_item, media_items
    ))

    media_id = anime_list_item_to_media_id(anilist_item, media_item)
    media_id = cast(MediaId, update_or_insert_item(media_id, media_ids))

    if anilist_item.myanimelist_id is not None:
        mal_id = anime_list_item_to_media_id(
            anilist_item, media_item, ListService.MYANIMELIST
        )
        update_or_insert_item(mal_id, media_ids)

    user_state = anilist_user_item_to_media_user_state(
        anilist_item, media_id, username.user
    )
    user_state = cast(MediaUserState, update_or_insert_item(
        user_state, media_user_states
    ))

    media_list = anilist_user_item_to_media_list(anilist_item, username.user)
    media_list = cast(MediaList, update_or_insert_item(
        media_list, media_lists
    ))

    media_list_item = MediaListItem(
        media_list_id=media_list.id,
        media_user_state_id=user_state.id
    )
    update_or_insert_item(media_list_item, media_list_items)
