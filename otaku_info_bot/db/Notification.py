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


class Notification(Base):
    """
    Models a generic Notification
    """

    __tablename__ = "notifications"
    """
    The name of the database table
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    """
    The ID of the notification
    """

    address_id = Column(Integer, ForeignKey("addressbook.id"))
    """
    The ID of the associated address
    """

    address = relationship("Address")
    """
    The associated address
    """

    entry_id = Column(Integer, ForeignKey("anilist_entries.id"))
    """
    The ID of the associated anilist entry
    """

    entry = relationship("AnilistEntry")
    """
    The associated anilist entry
    """

    user_progress = Column(Integer, default=0, nullable=False)
    """
    The user's current progress
    """

    last_update = Column(Integer, default=0, nullable=False)
    """
    The last notification update
    """

    user_score = Column(Integer, default=0, nullable=False)
    """
    Score that the user gave the entry
    """

    @property
    def diff(self) -> int:
        """
        The difference between the last update and the current entry value
        :return: The difference
        """
        return self.entry.latest - self.last_update

    @property
    def user_diff(self) -> bool:
        """
        :return: The difference between the user's progress and the latest
                 entry value
        """
        return self.entry.latest - self.user_progress

    def __str__(self) -> str:
        return "({})[{}]: {} (diff:{} [{}/{}])".format(
            self.id,
            self.address.address,
            self.entry.name,
            self.diff,
            self.last_update,
            self.entry.latest
        )
