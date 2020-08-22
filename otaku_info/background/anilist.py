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
from typing import List, Dict, Tuple, Optional, cast
from puffotter.flask.base import db, app
from otaku_info.db.MediaId import MediaId
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaListItem import MediaListItem
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.ServiceUsername import ServiceUsername
from otaku_info.external.anilist import load_anilist
from otaku_info.enums import ListService, MediaType
from otaku_info.utils.db.updater import update_or_insert_item
from otaku_info.utils.db.convert import anilist_item_to_media_id, \
    anilist_item_to_media_item, anilist_user_item_to_media_user_state, \
    anilist_user_item_to_media_list


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

    anilist_data = {
        username: {
            media_type: load_anilist(username.username, media_type)
            for media_type in MediaType
        }
        for username in usernames
    }
    media_items, media_ids, media_user_states, media_lists, media_list_items \
        = __load_existing()

    for username, anilist_info in anilist_data.items():
        for media_type, anilist_items in anilist_info.items():
            for anilist_item in anilist_items:
                media_item = anilist_item_to_media_item(anilist_item)
                media_item = cast(MediaItem, update_or_insert_item(
                    media_item, media_items
                ))
                media_id = anilist_item_to_media_id(anilist_item, media_item)
                media_id = cast(MediaId, update_or_insert_item(
                    media_id, media_ids
                ))
                user_state = anilist_user_item_to_media_user_state(
                    anilist_item, media_id, username.user
                )
                user_state = cast(MediaUserState, update_or_insert_item(
                    user_state, media_user_states
                ))
                media_list = anilist_user_item_to_media_list(
                    anilist_item, username.user
                )
                media_list = cast(MediaList, update_or_insert_item(
                    media_list, media_lists
                ))
                media_list_item = MediaListItem(
                    media_list_id=media_list.id,
                    media_user_state_id=user_state.id
                )
                update_or_insert_item(
                    media_list_item, media_list_items
                )
    db.session.commit()  # Commit Updates
    app.logger.info(f"Finished Anilist Update in {time.time() - start}s.")


def __load_existing() -> Tuple[
    Dict[Tuple, MediaItem],
    Dict[Tuple, MediaId],
    Dict[Tuple, MediaUserState],
    Dict[Tuple, MediaList],
    Dict[Tuple, MediaListItem]
]:
    """
    Loads current database contents, mapped to unique identifer tuples
    :return: The database contents
    """
    media_items: Dict[Tuple, MediaItem] = {
        x.identifier_tuple: x
        for x in MediaItem.query.options(
            db.joinedload(MediaItem.media_ids)
              .subqueryload(MediaId.media_user_states)
        ).all()
    }
    media_ids: Dict[Tuple, MediaId] = {}
    media_user_states: Dict[Tuple, MediaUserState] = {}
    for media_item in media_items.values():
        for media_id in media_item.media_ids:
            media_ids[media_id.identifier_tuple] = media_id
            for user_state in media_id.media_user_states:
                media_user_states[user_state.identifier_tuple] = user_state
    media_lists: Dict[Tuple, MediaList] = {
        x.identifier_tuple: x
        for x in MediaList.query.options(
            db.joinedload(MediaList.media_list_items)
        ).all()
    }
    media_list_items: Dict[Tuple, MediaListItem] = {}
    for media_list in media_lists.values():
        for list_item in media_list.media_list_items:
            media_list_items[list_item.identifier_tuple] = list_item

    return media_items, media_ids, media_user_states, \
        media_lists, media_list_items
