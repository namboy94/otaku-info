"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-web.

otaku-info-web is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-web is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-web.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import List, Dict, Optional, Union, Tuple
from puffotter.flask.base import db, app
from puffotter.flask.db.User import User
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.db.MediaList import MediaList
from otaku_info_web.db.MediaListItem import MediaListItem
from otaku_info_web.db.MediaUserState import MediaUserState
from otaku_info_web.db.ServiceUsername import ServiceUsername
from otaku_info_web.utils.anilist.AnilistItem import AnilistItem
from otaku_info_web.utils.anilist.api import load_anilist
from otaku_info_web.utils.enums import ListService, MediaType, MediaSubType


def fetch_anilist_data():
    """
    Retrieves all entries on the anilists of all users that provided
    an anilist username
    :return: None
    """
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
    media_ids = update_media_entries(anilist_data)
    update_media_user_entries(anilist_data, media_ids)
    update_media_lists(anilist_data)
    app.logger.debug("Completed anilist update")


def update_media_entries(
        anilist_data: Dict[
            ServiceUsername,
            Dict[MediaType, List[AnilistItem]]
        ]
) -> Dict[Tuple[int, MediaType], MediaId]:
    """
    Updates the media entries and anilist IDs
    :param anilist_data:
    :return:
    """
    media_ids = {
        (x.service_id, x.media_item.media_type): x for x in MediaId.query.all()
    }
    media_items = {
        (x.romaji_title, x.media_subtype): x for x in MediaItem.query.all()
    }
    updated: List[Union[Tuple[int, MediaType], Tuple[str, MediaSubType]]] = []

    for media_type in MediaType:

        anilist_entries: List[AnilistItem] = []
        for data in anilist_data.values():
            anilist_entries += data[media_type]

        for anilist_entry in anilist_entries:
            item_tuple \
                = (anilist_entry.romaji_title, anilist_entry.media_subtype)
            id_tuple = (anilist_entry.anilist_id, anilist_entry.media_type)

            media_item = media_items.get(item_tuple)
            media_id = media_ids.get(id_tuple)

            if item_tuple not in updated:
                media_item = update_media_item(anilist_entry, media_item)
                media_items[item_tuple] = media_item
                updated.append(item_tuple)
            if id_tuple not in updated:
                media_id = update_media_id(anilist_entry, media_item, media_id)
                media_ids[id_tuple] = media_id
                updated.append(id_tuple)

    db.session.commit()
    return media_ids


def update_media_user_entries(
        anilist_data: Dict[
            ServiceUsername,
            Dict[MediaType, List[AnilistItem]]
        ],
        media_ids: Dict[Tuple[int, MediaType], MediaId]
):
    """
    Updates the individual users' current state for media items in
    thei ranilist account.
    :param anilist_data: The anilist data to enter into the database
    :param media_ids: The anilist media IDs of the previously added media items
    :return: None
    """
    all_user_entries = {
        (x.media_id.service_id, x.media_id.media_item.media_type): x
        for x in MediaUserState.query.all()
    }

    for service_user, anilist in anilist_data.items():
        user = service_user.user
        user_entries = {
            x: y for x, y in all_user_entries.items()
            if y.user.username == service_user.user.username
        }
        updated = []

        for media_type, anilist_entries in anilist.items():
            for entry in anilist_entries:
                id_tuple = (entry.anilist_id, entry.media_type)

                if id_tuple in updated:
                    continue

                media_id = media_ids[id_tuple]
                user_entry = user_entries.get(id_tuple)
                update_media_user_state(entry, media_id, user, user_entry)

                updated.append(id_tuple)

        for id_tuple, user_entry in user_entries.items():
            if id_tuple not in updated:
                db.session.remove(user_entry)

    db.session.commit()


def update_media_lists(
        anilist_data: Dict[
            ServiceUsername,
            Dict[MediaType, List[AnilistItem]]
        ]
):
    """
    Updates the database for anilist user lists.
    This includes custom anilist lists.
    :param anilist_data: The anilist data to enter into the database
    :return: None
    """
    MediaListItem.query.delete()
    existing_lists = MediaList.query.all()
    all_user_states = {
        (x.media_id.service_id, x.media_id.media_item.media_type): x
        for x in MediaUserState.query.all()
    }

    for service_user, anilist in anilist_data.items():

        user_states = {
            x: y for x, y in all_user_states.items()
            if y.user.username == service_user.user.username
        }

        for media_type, entries in anilist.items():

            collected_list_names = []
            user_lists = {
                x.name: x for x in existing_lists
                if x.user_id == service_user.user_id
                and media_type == x.media_type
            }

            for entry in entries:
                if entry.list_name not in collected_list_names:
                    collected_list_names.append(entry.list_name)

                if entry.list_name not in user_lists:
                    user_list = MediaList(
                        user=service_user.user,
                        name=entry.list_name,
                        service=ListService.ANILIST,
                        media_type=media_type
                    )
                    db.session.add(user_list)
                    user_lists[entry.list_name] = user_list
                else:
                    user_list = user_lists[entry.list_name]

                state_tuple = (entry.anilist_id, entry.media_type)
                list_item = MediaListItem(
                    media_list=user_list,
                    media_user_state=user_states[state_tuple]
                )
                db.session.add(list_item)

            for list_name, user_list in user_lists.items():
                if list_name not in collected_list_names:
                    db.session.remove(user_list)

    db.session.commit()


def update_media_item(
        new_data: AnilistItem,
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
    return media_item


def update_media_id(
        new_data: AnilistItem,
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
    media_id.service_id = new_data.anilist_id

    if existing is None:
        db.session.add(media_id)
    return media_id


def update_media_user_state(
        new_data: AnilistItem,
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
    return media_user_state
