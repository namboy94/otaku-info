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

from otaku_info_web.utils.enums import MediaType


class AnilistListItem:
    """
    Class that models an anilist list item for a user
    Represents the information fetched using anilist's API
    """
    def __init__(
            self,
            anilist_id: int,
            media_type: MediaType,
            english_title: str,
            romaji_title: str,
            cover_url: str,
            chapters: int,
            episodes: int,
            status: str,
            score: int,
            progress: int,
            list_name: str
    ):
        self.anilist_id = anilist_id
        self.media_type = media_type
        self.english_title = english_title
        self.romaji_title = romaji_title
        self.cover_url = cover_url
        self.chapters = chapters
        self.episodes = episodes
        self.status = status
        self.score = score
        self.progress = progress
        self.list_name = list_name
