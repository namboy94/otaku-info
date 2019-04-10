"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of aniremind.

aniremind is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

aniremind is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with aniremind.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from kudubot.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Reminder(Base):
    """
    Models a reminder
    """

    __tablename__ = "reminders"
    """
    The table name
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    """
    The ID of the reminder
    """

    address_id = Column(Integer, ForeignKey("addressbook.id"))
    """
    The ID of the associated address
    """

    address = relationship("Address")
    """
    The associated address
    """

    show_name = Column(String(255), nullable=False)
    """
    The name of the show
    """

    last_episode = Column(Integer, default=0, nullable=False)
    """
    The last episode the user was reminded of
    """

    def __str__(self):
        """
        :return: A string representing the reminder
        """
        return "{}: {}".format(self.id, self.show_name)
