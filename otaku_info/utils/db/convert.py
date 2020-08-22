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

from puffotter.flask.db.User import User
from otaku_info.enums import ListService
from otaku_info.db.MediaId import MediaId
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.external.entities.AnilistItem import AnilistItem
from otaku_info.external.entities.AnilistUserItem import AnilistUserItem


def anilist_item_to_media_item(anilist_item: AnilistItem) -> MediaItem:
    """
    Converts an anilist item to a media item object
    :param anilist_item: The anilist item
    :return: The media item
    """
    return MediaItem(
        media_type=anilist_item.media_type,
        media_subtype=anilist_item.media_subtype,
        english_title=anilist_item.english_title,
        romaji_title=anilist_item.romaji_title,
        cover_url=anilist_item.cover_url,
        latest_release=anilist_item.latest_release,
        latest_volume_release=anilist_item.volumes,
        releasing_state=anilist_item.releasing_state
    )


def anilist_item_to_media_id(
        anilist_item: AnilistItem,
        media_item: MediaItem
) -> MediaId:
    """
    Converts an anilist item into a media id
    :param anilist_item: The anilist item
    :param media_item: The corresponding media item
    :return: The generated media id
    """
    return MediaId(
        media_item_id=media_item.id,
        service_id=str(anilist_item.anilist_id),
        service=ListService.ANILIST,
        media_type=media_item.media_type
    )


def anilist_user_item_to_media_user_state(
        anilist_user_item: AnilistUserItem,
        media_id: MediaId,
        user: User
) -> MediaUserState:
    """
    Generates a media user state based on an anilist user item
    :param anilist_user_item: The anilist user item
    :param media_id: The corresponding media id
    :param user: The corresponding user
    :return: The media user state
    """
    return MediaUserState(
        media_id_id=media_id.id,
        user_id=user.id,
        progress=anilist_user_item.progress,
        volume_progress=anilist_user_item.volume_progress,
        score=anilist_user_item.score,
        consuming_state=anilist_user_item.consuming_state
    )


def anilist_user_item_to_media_list(
        anilist_user_item: AnilistUserItem,
        user: User,
) -> MediaList:
    """
    Generates a media list from an anilist user item
    :param anilist_user_item: The anilist user item
    :param user: The corresponding user
    :return: The media list object
    """
    return MediaList(
        user_id=user.id,
        name=anilist_user_item.list_name,
        service=ListService.ANILIST,
        media_type=anilist_user_item.media_type
    )
