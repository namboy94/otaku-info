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
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class MangaUpdate(Base):
    """
    Models a manga update entry
    """

    __tablename__ = "manga_updates"
    """
    The table name
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    """
    The ID of the manga updater entry
    """

    address_id = Column(Integer, ForeignKey("addressbook.id"))
    """
    The ID of the associated address
    """

    address = relationship("Address")
    """
    The associated address
    """

    entry_id = Column(Integer, ForeignKey("manga_entries.id"))
    """
    The ID of the associated manga entry
    """

    entry = relationship("MangaEntry")
    """
    The associated manga entry
    """

    last_update = Column(Integer, default=0, nullable=False)
    """
    The last chapter update
    """

    @property
    def diff(self) -> int:
        """
        The difference between the last update and the current chapter
        :return: The difference
        """
        return self.entry.latest_chapter - self.last_update
