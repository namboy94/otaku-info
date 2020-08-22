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

from typing import Optional, Dict, Tuple
from puffotter.flask.base import db
from puffotter.flask.db.User import User
from otaku_info.db.ModelMixin import ModelMixin
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaId import MediaId
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.enums import ListService
from otaku_info.external.entities.AnilistItem import AnilistItem
from otaku_info.external.entities.AnilistUserItem import AnilistUserItem


def update_or_insert_item(
        to_add: ModelMixin,
        existing: Dict[Tuple, ModelMixin]
) -> ModelMixin:
    """
    Updates or creates an item that can be identified based on a unique tuple.
    :param to_add: The item to add
    :param existing: The existing items
    :return: The updated or created item
    """
    existing_item = existing.get(to_add.identifier_tuple)
    if existing_item is None:
        db.session.add(to_add)
    else:
        to_add.id = existing_item.id
        db.session.merge(to_add)
    db.session.commit()
    existing[to_add.identifier_tuple] = to_add
    return to_add


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
        db.session.commit()
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
