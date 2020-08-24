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

from typing import Optional
from puffotter.flask.db.User import User
from otaku_info.enums import ListService, MediaType, MediaSubType
from otaku_info.db.MediaId import MediaId
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.LnRelease import LnRelease
from otaku_info.external.entities.AnimeListItem import AnimeListItem
from otaku_info.external.entities.AnilistUserItem import AnilistUserItem
from otaku_info.external.entities.MangadexItem import MangadexItem
from otaku_info.external.entities.RedditLnRelease import RedditLnRelease


def anime_list_item_to_media_item(anime_list_item: AnimeListItem) -> MediaItem:
    """
    Converts an anime list item to a media item object
    :param anime_list_item: The anime list item
    :return: The media item
    """
    return MediaItem(
        media_type=anime_list_item.media_type,
        media_subtype=anime_list_item.media_subtype,
        english_title=anime_list_item.english_title,
        romaji_title=anime_list_item.romaji_title,
        cover_url=anime_list_item.cover_url,
        latest_release=anime_list_item.latest_release,
        latest_volume_release=anime_list_item.volumes,
        releasing_state=anime_list_item.releasing_state
    )


def mangadex_item_to_media_item(mangadex_item: MangadexItem) -> MediaItem:
    """
    Converts a mangadex item to a media item object
    :param mangadex_item: The mangadex item
    :return: The media item
    """
    return MediaItem(
        media_type=MediaType.MANGA,
        media_subtype=MediaSubType.MANGA,
        english_title=mangadex_item.title,
        romaji_title=mangadex_item.title,
        cover_url=mangadex_item.cover_url,
        latest_release=mangadex_item.total_chapters,
        latest_volume_release=None,
        releasing_state=mangadex_item.releasing_state
    )


def anime_list_item_to_media_id(
        anime_list_item: AnimeListItem,
        media_item: MediaItem,
        list_service: Optional[ListService] = None
) -> MediaId:
    """
    Converts an anime list item into a media id
    :param anime_list_item: The anime list item
    :param media_item: The corresponding media item
    :param list_service: Uses an extra ID with the specified list service
    :return: The generated media id
    """
    if list_service is not None:
        service_id = anime_list_item.extra_ids[list_service]
        service = ListService.MYANIMELIST
    else:
        service_id = anime_list_item.id
        service = ListService.ANILIST

    return MediaId(
        media_item_id=media_item.id,
        service_id=str(service_id),
        service=service,
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


def ln_release_from_reddit_item(
        ln_release: RedditLnRelease,
        media_item: Optional[MediaItem]
) -> LnRelease:
    """
    Creates an LnRelease object based on a RedditLnRelease object
    :param ln_release: The RedditLnRelease object
    :param media_item: An associated MediaItem
    :return: The LnRelease object
    """
    media_item_id = None if media_item is None else media_item.id
    return LnRelease(
        media_item_id=media_item_id,
        release_date_string=ln_release.release_date_string,
        series_name=ln_release.series_name,
        volume=ln_release.volume,
        publisher=ln_release.publisher,
        purchase_link=ln_release.purchase_link,
        digital=ln_release.digital,
        physical=ln_release.physical
    )
