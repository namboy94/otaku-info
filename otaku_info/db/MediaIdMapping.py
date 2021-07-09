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

from typing import List, TYPE_CHECKING, Optional
from jerrycan.base import db
from jerrycan.db.ModelMixin import ModelMixin
from otaku_info.enums import ListService
from otaku_info.db.MediaItem import MediaItem
from otaku_info.utils.urls import generate_service_icon_url,\
    generate_service_url
if TYPE_CHECKING:
    from otaku_info.db.MediaUserState import MediaUserState
    from otaku_info.db.MangaChapterGuess import MangaChapterGuess


class MediaIdMapping(ModelMixin, db.Model):
    """
    Database model to map media IDs to each other across services
    """

    __tablename__ = "media_id_mappings"
    """
    The name of the database table
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    media_item_id: int = db.Column(db.Integer, nullable=False)
    """
    The ID of the media item
    """

    primary_media_item: MediaItem = db.relationship(
        "MediaItem",
        back_populates="media_id_mappings"
    )
    """
    The media item
    """

    service: ListService = db.Column(db.Enum(ListService), nullable=False)
    """
    The service for which the ID mapping is done
    """

    service_id: str = db.Column(db.String(255), nullable=False)
    """
    The ID of the media item on the other service
    """

    media_user_states: List["MediaUserState"] = db.relationship(
        "MediaUserState", back_populates="media_id", cascade="all, delete"
    )
    """
    Media user states associated with this media ID
    """

    chapter_guess: Optional["MangaChapterGuess"] = db.relationship(
        "MangaChapterGuess",
        uselist=False,
        back_populates="media_id",
        cascade="all, delete"
    )
    """
    Chapter Guess for this media ID (Only applicable if this is a manga title)
    """

    def service_url(self) -> str:
        """
        :return: The URL to the series for the given service
        """
        return generate_service_url(
            self.service,
            self.media_type,
            self.service_id
        )

    @property
    def service_icon(self) -> str:
        """
        :return: The path to the service's icon file
        """
        return generate_service_icon_url(self.service)
