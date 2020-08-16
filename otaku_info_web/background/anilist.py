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
from typing import List, Dict, Optional, Tuple
from puffotter.flask.base import db, app
from puffotter.flask.db.User import User
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.db.MediaList import MediaList
from otaku_info_web.db.MediaListItem import MediaListItem
from otaku_info_web.db.MediaUserState import MediaUserState
from otaku_info_web.db.ServiceUsername import ServiceUsername
from otaku_info_web.utils.anilist.AnilistItem import AnilistUserItem
from otaku_info_web.utils.anilist.api import load_anilist
from otaku_info_web.utils.enums import ListService, MediaType, MediaSubType


def fetch_anilist_data():
    """
    Retrieves all entries on the anilists of all users that provided
    an anilist username
    :return: None
    """
    start = time.time()
    app.logger.debug("Starting Anilist Update")
    usernames: List[ServiceUsername] = \
        ServiceUsername.query.filter_by(service=ListService.ANILIST).all()
    anilist_data = {
        user: {
            media_type: load_anilist(user.username, media_type)
            for media_type in MediaType
        }
        for user in usernames
    }
    media_items, media_ids, media_user_states, media_lists, media_list_items\
        = load_existing()

    app.logger.debug("Updating Media Entries")
    update_media_entries(
        anilist_data, media_items, media_ids
    )
    app.logger.debug("Updating Media User States")
    update_media_user_entries(
        anilist_data, media_items, media_ids, media_user_states
    )
    app.logger.debug("Updating Media Lists")
    update_media_lists(
        anilist_data,
        media_items,
        media_ids,
        media_user_states,
        media_lists,
        media_list_items
    )
    app.logger.info(f"Completed anilist update in {time.time() - start}")


def update_media_entries(
        anilist_data: Dict[
            ServiceUsername,
            Dict[MediaType, List[AnilistUserItem]]
        ],
        media_items: Dict[Tuple[str, MediaType, MediaSubType, str], MediaItem],
        media_ids: Dict[Tuple[ListService, int], MediaId]
):
    """
    Updates the media entries and anilist IDs
    :param anilist_data: The anilist data to store
    :param media_items: The preloaded media items
    :param media_ids: The preloaded media IDs
    :return: None
    """
    updated_ids: List[Tuple[ListService, int]] = []
    updated_items: List[Tuple[str, MediaType, MediaSubType, str]] = []

    for media_type in MediaType:

        anilist_entries: List[AnilistUserItem] = []
        for data in anilist_data.values():
            anilist_entries += data[media_type]

        for anilist_entry in anilist_entries:
            item_tuple, media_item = fetch_media_item(
                anilist_entry, media_items
            )
            if item_tuple not in updated_items:
                media_item = update_media_item(anilist_entry, media_item)
                media_items[item_tuple] = media_item
                updated_items.append(item_tuple)

            id_tuple, media_id = fetch_media_id(
                anilist_entry, media_items, media_ids, media_item
            )
            assert id_tuple is not None

            if id_tuple not in updated_ids:
                media_item = media_items[item_tuple]
                media_id = update_media_id(anilist_entry, media_item, media_id)
                media_ids[id_tuple] = media_id
                updated_ids.append(id_tuple)

    db.session.commit()
    return media_ids


def update_media_user_entries(
        anilist_data: Dict[
            ServiceUsername,
            Dict[MediaType, List[AnilistUserItem]]
        ],
        media_items: Dict[Tuple[str, MediaType, MediaSubType, str], MediaItem],
        media_ids: Dict[Tuple[ListService, int], MediaId],
        media_user_states: Dict[Tuple[int, int], MediaUserState]
):
    """
    Updates the individual users' current state for media items in
    thei ranilist account.
    :param anilist_data: The anilist data to enter into the database
    :param media_items: Preloaded media items
    :param media_ids: Preloaded media IDs
    :param media_user_states: Preloaded media user states
    :return: None
    """
    updated: List[Tuple[int, int]] = []

    for service_user, anilist in anilist_data.items():
        user_states = {
            x: y for x, y in media_user_states.items()
            if y.user_id == service_user.user_id
        }

        for media_type, anilist_entries in anilist.items():
            for entry in anilist_entries:
                id_tuple, media_id = \
                    fetch_media_id(entry, media_items, media_ids)
                assert media_id is not None

                user_state_id = (media_id.id, service_user.user_id)

                if user_state_id in updated:
                    continue

                media_user_state = media_user_states.get(user_state_id)

                media_user_state = update_media_user_state(
                    entry, media_id, service_user.user, media_user_state
                )

                updated.append(user_state_id)
                media_user_states[user_state_id] = media_user_state

        for user_state_tuple, user_state in user_states.items():
            if user_state_tuple not in updated:
                db.session.delete(user_state)
                media_user_states.pop(user_state_tuple)

        db.session.commit()


def update_media_lists(
        anilist_data: Dict[
            ServiceUsername,
            Dict[MediaType, List[AnilistUserItem]]
        ],
        media_items: Dict[Tuple[str, MediaType, MediaSubType, str], MediaItem],
        media_ids: Dict[Tuple[ListService, int], MediaId],
        media_user_states: Dict[Tuple[int, int], MediaUserState],
        media_lists: Dict[Tuple[str, int, ListService, MediaType], MediaList],
        media_list_items: Dict[Tuple[int, int], MediaListItem]
):
    """
    Updates the database for anilist user lists.
    This includes custom anilist lists.
    :param anilist_data: The anilist data to enter into the database
    :param media_items: Preloaded media items
    :param media_ids: Preloaded media IDs
    :param media_user_states: The current media user states in the database
    :param media_lists: The media lists currently in the database
    :param media_list_items: The media list items currently in the database
    :return: None
    """
    list_tuples_to_remove = list(media_lists.keys())
    list_item_tuples_to_remove = list(media_list_items.keys())

    for service_user, anilist in anilist_data.items():
        for media_type, entries in anilist.items():
            for entry in entries:

                list_tuple = (
                    entry.list_name,
                    service_user.user_id,
                    ListService.ANILIST,
                    media_type
                )
                if list_tuple in list_tuples_to_remove:
                    list_tuples_to_remove.remove(list_tuple)
                media_list = media_lists.get(list_tuple)

                if media_list is None:
                    media_list = MediaList(
                        user_id=service_user.user_id,
                        name=entry.list_name,
                        service=ListService.ANILIST,
                        media_type=media_type
                    )
                    db.session.add(media_list)
                    db.session.commit()
                    media_lists[list_tuple] = media_list

                _, media_id = fetch_media_id(entry, media_items, media_ids)
                assert media_id is not None

                state_tuple = (media_id.id, service_user.user_id)
                media_user_state = media_user_states[state_tuple]

                list_item_tuple = (media_list.id, media_user_state.id)
                if list_item_tuple in list_item_tuples_to_remove:
                    list_item_tuples_to_remove.remove(list_item_tuple)

                if list_item_tuple not in media_list_items:
                    list_item = MediaListItem(
                        media_list=media_list,
                        media_user_state=media_user_state
                    )
                    db.session.add(list_item)

            db.session.commit()

    for list_tuple in list_tuples_to_remove:
        if list_tuple in media_lists:
            db.session.delete(media_lists.pop(list_tuple))
    for list_item_tuple in list_item_tuples_to_remove:
        if list_item_tuple in media_list_items:
            db.session.delete(media_list_items.pop(list_item_tuple))

    db.session.commit()


def load_existing() -> Tuple[
    Dict[Tuple[str, MediaType, MediaSubType, str], MediaItem],
    Dict[Tuple[ListService, int], MediaId],
    Dict[Tuple[int, int], MediaUserState],
    Dict[Tuple[str, int, ListService, MediaType], MediaList],
    Dict[Tuple[int, int], MediaListItem]
]:
    """
    Loads current database contents, mapped to unique identifer tuples
    :return: The database contents
    """
    app.logger.debug("Loading Existing data for anilist update")
    media_items: Dict[Tuple[str, MediaType, MediaSubType, str], MediaItem] = {
        (x.romaji_title, x.media_type, x.media_subtype, x.cover_url): x
        for x in MediaItem.query.all()
    }
    app.logger.debug("Finished loading MediaItems")
    media_ids: Dict[Tuple[ListService, int], MediaId] = {
        (x.service, x.media_item_id): x
        for x in MediaId.query.all()
    }
    app.logger.debug("Finished loading MediaIds")
    media_user_states: Dict[Tuple[int, int], MediaUserState] = {
        (x.media_id_id, x.user_id): x
        for x in MediaUserState.query.all()
    }
    app.logger.debug("Finished loading MediaUserStates")
    media_lists: Dict[Tuple[str, int, ListService, MediaType], MediaList] = {
        (x.name, x.user_id, x.service, x.media_type): x
        for x in MediaList.query.all()
    }
    app.logger.debug("Finished loading MediaLists")
    media_list_items: Dict[Tuple[int, int], MediaListItem] = {
        (x.media_list_id, x.media_user_state_id): x
        for x in MediaListItem.query.all()
    }
    app.logger.debug("Finished loading MediaListItems")
    return media_items, media_ids, media_user_states, \
        media_lists, media_list_items


def fetch_media_item(
        anilist_entry: AnilistUserItem,
        media_items: Dict[Tuple[str, MediaType, MediaSubType, str], MediaItem],
) -> Tuple[
    Tuple[str, MediaType, MediaSubType, str],
    Optional[MediaItem]
]:
    """
    Retrieves an existing media item based on anilist data
    :param anilist_entry: The anilist entry to use
    :param media_items: The preloaded media items
    :return: The media item, or None if none exists
    """
    item_tuple = (
        anilist_entry.romaji_title,
        anilist_entry.media_type,
        anilist_entry.media_subtype,
        anilist_entry.cover_url
    )
    return item_tuple, media_items.get(item_tuple)


def fetch_media_id(
        anilist_entry: AnilistUserItem,
        media_items: Dict[Tuple[str, MediaType, MediaSubType, str], MediaItem],
        media_ids: Dict[Tuple[ListService, int], MediaId],
        media_item: Optional[MediaId] = None
) -> Tuple[Optional[Tuple[ListService, int]], Optional[MediaItem]]:
    """
    Retrieves an existing media ID based on anilist data
    :param anilist_entry: The anilist entry to use
    :param media_items: The preloaded media items
    :param media_ids: The preloaded media IDs
    :param media_item: Optional media item associated with the ID.
                       If not provided, will figure out using anilist data
    :return: The media ID, or None if none exists
    """
    if media_item is None:
        _, media_item = fetch_media_item(anilist_entry, media_items)
    if media_item is None:
        return None, None
    else:
        id_tuple = (
            ListService.ANILIST,
            media_item.id
        )
        return id_tuple, media_ids.get(id_tuple)


def update_media_item(
        new_data: AnilistUserItem,
        existing: Optional[MediaItem]
) -> MediaItem:
    """
    Updates or creates MediaItem database entries based on anilist data
    :param new_data: The new anilist data
    :param existing: The existing database entry. If None, will be created
    :return: The updated/created MediaItem object
    """
    media_item = MediaItem() if existing is None else existing
    media_item.media_type = new_data.media_type
    media_item.media_subtype = new_data.media_subtype
    media_item.english_title = new_data.english_title
    media_item.romaji_title = new_data.romaji_title
    media_item.cover_url = new_data.cover_url
    media_item.latest_release = new_data.latest_release
    media_item.releasing_state = new_data.releasing_state

    if existing is None:
        db.session.add(media_item)
        db.session.commit()
    return media_item


def update_media_id(
        new_data: AnilistUserItem,
        media_item: MediaItem,
        existing: Optional[MediaId]
) -> MediaId:
    """
    Updates/Creates a MediaId database entry based on anilist data
    :param new_data: The anilist data to use
    :param media_item: The media item associated with the ID
    :param existing: The existing database entry. If None, will be created
    :return: The updated/created MediaId object
    """
    media_id = MediaId() if existing is None else existing
    media_id.media_item = media_item
    media_id.service = ListService.ANILIST
    media_id.service_id = str(new_data.anilist_id)

    if existing is None:
        db.session.add(media_id)
        db.session.commit()
    return media_id


def update_media_user_state(
        new_data: AnilistUserItem,
        media_id: MediaId,
        user: User,
        existing: Optional[MediaUserState]
) -> MediaUserState:
    """
    Updates or creates a MediaUserState entry in the database
    :param new_data: The new anilist data
    :param media_id: The media ID of the anilist media item
    :param user: The user associated with the data
    :param existing: The existing database entry. If None, will be created
    :return: The updated/created MediaUserState object
    """
    media_user_state = MediaUserState() if existing is None else existing
    media_user_state.media_id = media_id
    media_user_state.consuming_state = new_data.consuming_state
    media_user_state.score = new_data.score
    media_user_state.progress = new_data.progress
    media_user_state.user = user

    if existing is None:
        db.session.add(media_user_state)
        db.session.commit()
    return media_user_state
