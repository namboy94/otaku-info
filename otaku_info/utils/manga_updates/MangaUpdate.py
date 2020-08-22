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

from flask import url_for
from typing import Optional, List, Tuple, Dict, Any
from otaku_info.enums import ListService, MediaType
from otaku_info.utils.db_model_helper import build_service_url


class MangaUpdate:
    """
    Class that encapsulates important data to display for manga updates
    """

    def __init__(
            self,
            media_item_id: int,
            title: str,
            cover_url: str,
            latest_release: int,
            progress: int,
            score: int,
            chapter_guess: Optional[int],
            related_ids: List[Tuple[ListService, str]]
    ):
        """
        Initializes the MangaUpdate object
        :param media_item_id: The media item ID
        :param title: The title of the update
        :param cover_url: The URL for the media item's cover
        :param latest_release: The latest known released chapter
        :param progress: The user's current progress
        :param score: The user's score for this entry
        :param chapter_guess: The current chapter guess
        :param related_ids: Related service IDs
        """
        self.media_item_id = media_item_id
        self.title = title
        self.cover_url = cover_url
        self.score = score
        self.progress = progress
        self.related_ids = [RelatedMangaId(*args) for args in related_ids]
        self.url = url_for("media.media", media_item_id=media_item_id)

        if chapter_guess is None:
            self.latest = latest_release
        else:
            self.latest = chapter_guess

        if self.latest is None:
            self.latest = 0
        if self.progress is None:
            self.progress = 0

        if self.latest < self.progress:
            self.latest = self.progress

        self.diff = self.latest - self.progress

    def __json__(self) -> Dict[str, Any]:
        """
        Converts the object into a JSON-compatible dictionary
        :return: The JSON-compatible dictionary
        """
        return {
            "title": self.title,
            "cover_url": self.cover_url,
            "score": self.score,
            "progress": self.progress,
            "related_ids": [
                {
                    "service": x.service.value,
                    "id": x.service_id,
                    "url": x.url,
                    "icon": x.icon
                }
                for x in self.related_ids
            ],
            "latest": self.latest,
            "diff": self.diff
        }


class RelatedMangaId:
    """
    Class that encapslates attributes for a related manga ID
    """

    def __init__(self, service: ListService, service_id: str):
        """
        Intializes the RelatedMangaId object
        :param service: The service of the related manga ID
        :param service_id: The ID on that service
        """
        self.service = service
        self.service_id = service_id
        self.url = build_service_url(MediaType.MANGA, service, service_id)
        self.icon = url_for(
            "static", filename="service_logos/" + service.value + ".png"
        )
