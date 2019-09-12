"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-bot.

otaku-info-bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-bot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from kudubot.db import Base
from sqlalchemy import Column, Integer, String


class AnilistEntry(Base):
    """
    Models an anilist entry
    """

    __tablename__ = "anilist_entries"
    """
    The name of the database table
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    """
    The ID of the entry
    """

    anilist_id = Column(Integer, nullable=False)
    """
    The anilist ID of the entry
    """

    name = Column(String(255), nullable=False)
    """
    The name of the series
    """

    media_type = Column(String(5), nullable=False)
    """
    The media type of the entry
    """

    latest = Column(Integer, default=0, nullable=False)
    """
    The most recently released episode/chapter
    """

    @property
    def anilist_url(self) -> str:
        """
        :return: The URL to the anilist page
        """
        return "https://anilist.co/{}/{}".format(
            self.media_type, self.anilist_id
        )
