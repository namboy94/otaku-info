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
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr


class NotificationConfig:
    """
    Models generic anilist-related notification configurations
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    """
    The ID of the config
    """

    @declared_attr
    def address_id(self):
        """
        The ID of the associated address
        """
        return Column(Integer, ForeignKey("addressbook.id"))

    @declared_attr
    def address(self):
        """
        The associated address
        """
        return relationship("Address")

    anilist_username = Column(String(255), nullable=False)
    """
    The anilist username to use
    """

    list_name = Column(String(255), nullable=False)
    """
    The anilist list
    """

    @classmethod
    def default_list_name(cls) -> str:
        """
        :return: The default list name
        """
        raise NotImplementedError()

    @classmethod
    def media_type(cls) -> str:
        """
        :return: The media type
        """
        raise NotImplementedError()


class AnimeNotificationConfig(NotificationConfig, Base):
    """
    Configuration for anime updates
    """

    __tablename__ = "anime_notification_configs"
    """
    The table name
    """

    @classmethod
    def default_list_name(cls) -> str:
        """
        :return: The default list name
        """
        return "Watching"

    @classmethod
    def media_type(cls) -> str:
        """
        :return: The media type
        """
        return "anime"


class MangaNotificationConfig(NotificationConfig, Base):
    """
    Configuration for manga reminders
    """

    __tablename__ = "manga_notification_configs"
    """
    The table name
    """

    @classmethod
    def default_list_name(cls) -> str:
        """
        :return: The default list name
        """
        return "Reading"

    @classmethod
    def media_type(cls) -> str:
        """
        :return: The media type
        """
        return "manga"
