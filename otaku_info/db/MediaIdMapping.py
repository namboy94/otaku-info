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

from jerrycan.base import db
from jerrycan.db.ModelMixin import NoIDModelMixin
from otaku_info.enums import ListService, MediaType
from otaku_info.db.MediaItem import MediaItem
from otaku_info.utils.urls import generate_service_icon_url,\
    generate_service_url


class MediaIdMapping(NoIDModelMixin, db.Model):
    """
    Database model to map media IDs to each other across services
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "media_id_mappings"
    __table_args__ = (db.ForeignKeyConstraint(
        ("service", "service_id", "media_type"),
        (MediaItem.service, MediaItem.service_id, MediaItem.media_type)
    ),)

    parent_service: ListService = \
        db.Column(db.Enum(ListService), primary_key=True)
    parent_service_id: str = db.Column(db.String(255), primary_key=True)
    media_type: MediaType = db.Column(db.Enum(MediaType), primary_key=True)
    service: ListService = db.Column(db.Enum(ListService), primary_key=True)

    service_id: str = db.Column(db.String(255), nullable=False)

    media_item: MediaItem = db.relationship(
        "MediaItem", back_populates="media_user_states"
    )

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
