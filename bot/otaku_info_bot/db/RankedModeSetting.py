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
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class RankedModeSetting(Base):
    """
    Stores a user's preference for ranked mode
    """

    __tablename__ = "ranked_mode_settings"
    """
    The name of the database table
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    """
    The ID of the setting
    """

    address_id = Column(Integer, ForeignKey("addressbook.id"))
    """
    The ID of the associated address
    """

    address = relationship("Address")
    """
    The associated address
    """

    value = Column(Boolean, nullable=False, default=False)
    """
    The current value of the setting
    """
