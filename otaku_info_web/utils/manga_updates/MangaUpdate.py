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

    @staticmethod
    def get_icon(list_service: ListService):
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
                                     "icon/apple-touch-icon-256.png",
            ListService.MANGAUPDATES: "https://images-wixmp-ed30a86b8c4ca8877"
                                      "73594c2.wixmp.com/f/c62ca132-232a-4540"
                                      "-9634-7a23e0be45ee/d14dc73-b4b9a8e7-f4"
                                      "5f-4663-8d2d-4ddab19d3e2c.png/v1/fill/"
                                      "w_394,h_434,strp/baka_logo_by_baka_y2k"
                                      "7_d14dc73-fullview.png?token=eyJ0eXAiO"
                                      "iJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOi"
                                      "J1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWY"
                                      "wZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFw"
                                      "cDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYT"
                                      "BkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9"
                                      "NDM0IiwicGF0aCI6IlwvZlwvYzYyY2ExMzItMj"
                                      "MyYS00NTQwLTk2MzQtN2EyM2UwYmU0NWVlXC9k"
                                      "MTRkYzczLWI0YjlhOGU3LWY0NWYtNDY2My04ZD"
                                      "JkLTRkZGFiMTlkM2UyYy5wbmciLCJ3aWR0aCI6"
                                      "Ijw9Mzk0In1dXSwiYXVkIjpbInVybjpzZXJ2aW"
                                      "NlOmltYWdlLm9wZXJhdGlvbnMiXX0.VtNvtNhS"
                                      "7ZiWa7VYe-ATH8ps_UYcTg7lwkTXsIAT0rs"
        }.get(list_service, url_for("static", filename='logo.png'))
