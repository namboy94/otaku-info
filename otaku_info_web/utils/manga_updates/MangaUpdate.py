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

from flask import url_for
from typing import Optional, Dict
from otaku_info_web.db.MangaChapterGuess import MangaChapterGuess
from otaku_info_web.db.MediaListItem import MediaListItem
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.utils.enums import ListService


class MangaUpdate:
    """
    Class that encapsulates important data to display for manga updates
    """

    def __init__(
            self,
            list_item: MediaListItem,
            chapter_guess: Optional[MangaChapterGuess],
            service_ids: Dict[ListService, MediaId]
    ):
        """
        Initializes the MangaUpdate object
        :param list_item: The list item to display
        :param chapter_guess: The corresponding chapter guess
        :param service_ids: Service IDS for this manga update entry
        """
        media_item = list_item.media_user_state.media_id.media_item
        self.title = media_item.title
        self.cover_url = media_item.cover_url
        self.url = list_item.media_user_state.media_id.service_url
        self.score = list_item.media_user_state.score
        self.progress = list_item.media_user_state.progress
        self.service_ids = service_ids

        if chapter_guess is None or chapter_guess.guess is None:
            self.latest = media_item.latest_release
        else:
            self.latest = chapter_guess.guess

        if self.latest is None:
            self.latest = 0
        if self.progress is None:
            self.progress = 0

        if self.latest < self.progress:
            self.latest = self.progress

        self.diff = self.latest - self.progress

    def get_icon(self, list_service: ListService):
        """
        Retrieves the icon for a list service
        :param list_service: The list service for which to retrieve the icon
        :return: The URL to the icon file
        """
        return {
            ListService.ANILIST: "https://pbs.twimg.com/profile_images/"
                                 "1236103622636834816/5TFL-AFz_400x400.png",
            ListService.MANGADEX: "https://i.pinimg.com/originals/73/9d/1b/"
                                  "739d1bc55429f8aeb516752c356c343c.png",
            ListService.MYANIMELIST: "https://cdn.myanimelist.net/img/sp/"
                                     "icon/apple-touch-icon-256.png"
        }.get(list_service, url_for("static", filename='logo.png'))
