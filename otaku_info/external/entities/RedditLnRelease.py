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

from datetime import datetime
from typing import Optional, List
from bs4.element import Tag
from otaku_info.utils.dates import map_month_name_to_month_number
from otaku_info.external.anilist import load_anilist_info
from otaku_info.enums import ListService, MediaType


class RedditLnRelease:
    """
    Object that acts as a wrapper around a light novel release on reddit.com
    """

    def __init__(
            self,
            series_name: str,
            year: int,
            release_date_string: str,
            volume: str,
            publisher: Optional[str],
            purchase_link: Optional[str],
            info_link: Optional[str],
            digital: bool,
            physical: bool
    ):
        """
        Initializes the object
        :param series_name: The name of the series
        :param year: The year of release
        :param release_date_string: The month and day of release
        :param volume: The volume number
        :param publisher: The publisher of the release
        :param purchase_link: A purchase link for the release
        :param info_link: Link to information for the release
        :param digital: Whether or not the release is digital
        :param physical: Whether or not the release is physical
        """
        self.series_name = series_name
        self.volume = volume
        self.publisher = publisher
        self.purchase_link = purchase_link
        self.info_link = info_link
        self.digital = digital
        self.physical = physical
        self.year = year
        self._release_date_string = release_date_string

    @property
    def release_date(self) -> datetime:
        """
        :return: The release date as a datetime object
        """
        month_name, day_string = self._release_date_string.split(" ")
        month = map_month_name_to_month_number(month_name)
        if month is None:
            month = 1
        try:
            day = int(day_string)
        except ValueError:
            day = 1
        return datetime(year=self.year, month=month, day=day)

    @property
    def release_date_string(self) -> str:
        """
        :return: The release date as a string (ISO 8601)
        """
        return self.release_date.strftime("%Y-%m-%d")

    @property
    def myanimelist_id(self) -> Optional[int]:
        """
        :return: The myanimelist ID, if available
        """
        if self.info_link is None or "myanimelist.net" not in self.info_link:
            return None

        url_parts = self.info_link.split("/")
        index = -1
        while not url_parts[index].isdigit():
            index -= 1
        return int(url_parts[index])

    @property
    def anilist_id(self) -> Optional[int]:
        """
        :return: The anilist ID, if available
        """
        if self.myanimelist_id is None:
            return None
        anilist_info = load_anilist_info(
            self.myanimelist_id, MediaType.MANGA, ListService.MYANIMELIST
        )
        if anilist_info is not None:
            return anilist_info.id
        else:
            return None

    @classmethod
    def from_parts(cls, year: int, parts: List[Tag]) -> "RedditLnRelease":
        """
        Generates a reddit LN release from BeautifulSoup td tags
        :param year: The year of the release
        :param parts: The td tags
        :return: The reddit ln release
        """
        purchase_link_item = parts[3].find("a")
        purchase_link = None
        if purchase_link_item is not None:
            purchase_link = purchase_link_item["href"]

        info_link_item = parts[1].find("a")
        info_link: Optional[str] = None
        if info_link_item is not None:
            info_link = info_link_item["href"]

        digital = "digital" in parts[4].text.lower()
        physical = "physical" in parts[4].text.lower()

        return cls(
            series_name=parts[1].text,
            year=year,
            release_date_string=parts[0].text,
            volume=parts[2].text,
            publisher=parts[3].text,
            purchase_link=purchase_link,
            info_link=info_link,
            digital=digital,
            physical=physical
        )
