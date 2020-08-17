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
from datetime import datetime
from otaku_info.utils.reddit.dates import map_month_name_to_month_number


class LnRelease:
    """
    Class that encapsulates data pertaining to a light novel release
    """

    def __init__(
            self,
            year: int,
            release_date_string: str,
            series_name: str,
            volume: str,
            publisher: Optional[str],
            purchase_link: Optional[str],
            info_link: Optional[str],
            digital: bool,
            physical: bool
    ):
        self.year = year
        self.release_date_string = release_date_string
        self.series_name = series_name
        self.volume = volume
        self.publisher = publisher
        self.purchase_link = purchase_link
        self.info_link = info_link
        self.digital = digital
        self.physical = physical

    @property
    def release_date(self) -> datetime:
        """
        :return: The release date as a datetime object
        """
        month, day = self.release_date_string.split(" ")
        month_number = map_month_name_to_month_number(month)
        try:
            day_number = int(day)
        except ValueError:
            day_number = 1
        return datetime(year=self.year, month=month_number, day=day_number)

    @property
    def release_date_iso(self) -> str:
        """
        The ISO date string for the release date
        """
        return self.release_date.strftime("%Y-%m-%d")

    @property
    def myanimelist_id(self) -> Optional[int]:
        """
        :return: The myanimelist ID if available
        """
        if self.info_link is not None and "myanimelist.net" in self.info_link:
            parts = self.info_link.split("/")
            index = -1
            while not parts[index].isdigit():
                index -= 1
            return int(parts[index])
        else:
            return None

    @property
    def lndb_id(self) -> Optional[str]:
        """
        :return: The LNDB ID if available
        """
        if self.info_link is not None and "lndb.info" in self.info_link:
            return self.info_link.split("/")[-1]
        else:
            return None
