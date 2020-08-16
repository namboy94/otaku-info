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
from typing import Dict, Any
from puffotter.flask.base import db
from puffotter.flask.db.ModelMixin import ModelMixin
from otaku_info_web.utils.enums import ListService
from otaku_info_web.utils.db_model_helper import build_service_url
from otaku_info_web.db.MediaItem import MediaItem


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
            name="unique_media_id"
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

    media_item_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_items.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the media item referenced by this ID
    """

    media_item: MediaItem = db.relationship(
        "MediaItem",
        backref=db.backref("media_ids", lazy=True, cascade="all,delete")
    )
    """
    The media item referenced by this ID
    """

    service_id: str = db.Column(db.String(255), nullable=False)
    """
    The ID of the media item on the external service
    """

    service: ListService = db.Column(db.Enum(ListService), nullable=False)
    """
    The service for which this object represents an ID
    """

    @property
    def service_url(self) -> str:
        """
        :return: The URL to the series for the given service
        """
        return build_service_url(
            self.media_item.media_type, self.service, self.service_id
        )

    @property
    def service_icon(self) -> str:
        """
        :return: The path to the service's icon file
        """
        return url_for(
            "static", filename="service_logos/" + self.service.value + ".png"
        )

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
            "service": self.service.value
        }
        if include_children:
            data["media_item"] = self.media_item.__json__(include_children)
        return data
