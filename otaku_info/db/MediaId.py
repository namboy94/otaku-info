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
from typing import Dict, Any, List, TYPE_CHECKING, Tuple, Optional
from jerrycan.base import db
from otaku_info.db.ModelMixin import ModelMixin
from otaku_info.enums import ListService, MediaType, MediaSubType
from otaku_info.mappings import list_service_url_formats
from otaku_info.db.MediaItem import MediaItem
if TYPE_CHECKING:
    from otaku_info.db.MediaUserState import MediaUserState
    from otaku_info.db.MangaChapterGuess import MangaChapterGuess


class MediaId(ModelMixin, db.Model):
    """
    Database model for media IDs.
    These are used to map media items to their corresponding external
    IDS on external sites.
    """

    __tablename__ = "media_ids"
    """
    The name of the database table
    """

    __table_args__ = (
        db.UniqueConstraint(
            "media_item_id",
            "service",
            name="unique_media_item_service_id"
        ),
        db.UniqueConstraint(
            "media_type",
            "service",
            "service_id",
            name="unique_service_id"
        ),
        db.ForeignKeyConstraint(
            [
                "media_item_id",
                "media_type",
                "media_subtype"
            ],
            [
                "media_items.id",
                "media_items.media_type",
                "media_items.media_subtype"
            ]
        ),
    )
    """
    Makes sure that objects that should be unique are unique
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
    The ID of the media item referenced by this ID
    """

    media_item: MediaItem = db.relationship(
        "MediaItem",
        back_populates="media_ids"
    )
    """
    The media item referenced by this ID
    """

    media_type: MediaType = db.Column(db.Enum(MediaType), nullable=False)
    """
    The media type of the list item
    """

    media_subtype: MediaSubType = \
        db.Column(db.Enum(MediaSubType), nullable=False)
    """
    The media subtype of the list item
    """

    service_id: str = db.Column(db.String(255), nullable=False)
    """
    The ID of the media item on the external service
    """

    service: ListService = db.Column(db.Enum(ListService), nullable=False)
    """
    The service for which this object represents an ID
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

    @property
    def service_url(self) -> str:
        """
        :return: The URL to the series for the given service
        """
        url_format = list_service_url_formats[self.service]
        url = url_format \
            .replace("@{media_type}", f"{self.media_type.value}") \
            .replace("@{id}", self.service_id)
        return url

    @property
    def service_icon(self) -> str:
        """
        :return: The path to the service's icon file
        """
        return url_for(
            "static", filename=f"service_logos/{self.service.value}.png"
        )

    @property
    def identifier_tuple(self) -> Tuple[MediaType, ListService, str]:
        """
        :return: A tuple that uniquely identifies this database entry
        """
        return self.media_type, self.service, self.service_id

    def update(self, new_data: "MediaId"):
        """
        Updates the data in this record based on another object
        :param new_data: The object from which to use the new values
        :return: None
        """
        self.media_item_id = new_data.media_item_id
        self.media_type = new_data.media_type
        self.service = new_data.service
        self.service_id = new_data.service_id

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models
                                 will be included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "media_item_id": self.media_item_id,
            "service_id": self.service_id,
            "service": self.service.value,
            "media_type": self.media_type.value,
            "media_subtype": self.media_subtype.value
        }
        if include_children:
            data["media_item"] = self.media_item.__json__(include_children)
        return data
