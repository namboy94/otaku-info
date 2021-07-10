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

from otaku_info.db import MediaItem, MediaUserState
from otaku_info.enums import ListService, MediaType, MediaSubType
from otaku_info.external.entities.AnilistUserItem import AnilistUserItem
from otaku_info.external.entities.AnimeListItem import AnimeListItem
from otaku_info.external.entities.MangadexItem import MangadexItem


def anime_list_item_to_media_item(item: AnimeListItem) -> MediaItem:
    """
    Converts an Anime List Item to a Media Item
    :param item: The anime list item to convert
    :return: The resulting MediaItem
    """
    return MediaItem(
        service=item.service,
        service_id=str(item.id),
        media_type=item.media_type,
        media_subtype=item.media_subtype,
        english_title=item.english_title,
        romaji_title=item.romaji_title,
        cover_url=item.cover_url,
        latest_release=item.latest_release,
        latest_volume_release=item.volumes,
        next_episode=item.next_episode,
        next_episode_airing_time=item.next_episode_airing_time,
        releasing_state=item.releasing_state
    )


def anilist_user_item_to_media_user_state(
        anilist_user_item: AnilistUserItem,
        user_id: int
):
    """
    Converts an anilist user item to a MediaUserState entry
    :param anilist_user_item: The item to convert
    :param user_id: The ID of the user
    :return:
    """
    return MediaUserState(
        service=anilist_user_item.service,
        service_id=str(anilist_user_item.id),
        media_type=anilist_user_item.media_type,
        user_id=user_id,
        progress=anilist_user_item.progress,
        volume_progress=anilist_user_item.volume_progress,
        score=anilist_user_item.score,
        consuming_state=anilist_user_item.consuming_state
    )


def mangadex_item_to_media_item(mangadex_item: MangadexItem) -> MediaItem:
    """
    Converts a mangadex item to a media item
    :param mangadex_item: The mangadex item to convert
    :return: The media item
    """
    return MediaItem(
        service=ListService.MANGADEX,
        service_id=mangadex_item.mangadex_id,
        media_type=MediaType.MANGA,
        media_subtype=MediaSubType.MANGA,
        english_title=mangadex_item.english_title,
        romaji_title=mangadex_item.romaji_title,
        cover_url=mangadex_item.cover_url,
        latest_release=mangadex_item.total_chapters,
        releasing_state=mangadex_item.releasing_state
    )
