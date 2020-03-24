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
    The update goes like this:
      1. Create or update media items and anilist media IDs
      2. Create or update media user entries
      3. Create or update user list and user list entries
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
    # TODO Update user entries
    # TODO Update user lists
    # TODO Update user list entries
    app.logger.debug("Completed anilist update")


def update_media_entries(
        anilist_data: Dict[
            ServiceUsername,
            Dict[MediaType, List[AnilistItem]]
        ]
) -> List[MediaId]:
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
    return list(media_ids.values())


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
