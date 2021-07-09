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

import re
from datetime import datetime
from typing import Optional
from jerrycan.base import db
from jerrycan.db.ModelMixin import NoIDModelMixin
from otaku_info.db.MediaItem import MediaItem
from otaku_info.enums import MediaType, ListService


class LnRelease(NoIDModelMixin, db.Model):
    """
    Database model that keeps track of light novel releases
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "ln_releases"
    __table_args__ = (db.ForeignKeyConstraint(
        ("service", "service_id", "media_type"),
        (MediaItem.service, MediaItem.service_id, MediaItem.media_type)
    ),)

    service: ListService = db.Column(db.Enum(ListService), primary_key=True)
    service_id: str = db.Column(db.String(255), primary_key=True)
    media_type: MediaType = db.Column(db.Enum(MediaType), primary_key=True)
    volume: str = db.Column(db.String(255), primary_key=True)

    release_date_string: str = db.Column(db.String(10), nullable=False)
    series_name: str = db.Column(db.String(255), nullable=False)
    publisher: Optional[str] = db.Column(db.String(255), nullable=True)
    purchase_link: Optional[str] = db.Column(db.String(255), nullable=True)
    digital: bool = db.Column(db.Boolean, nullable=False)
    physical: bool = db.Column(db.Boolean, nullable=False)

    media_item: MediaItem = db.relationship(
        "MediaItem", back_populates="media_user_states"
    )

    @property
    def release_date(self) -> datetime:
        """
        :return: The release date as a datetime object
        """
        return datetime.strptime(self.release_date_string, "%Y-%m-%d")

    @property
    def volume_number(self) -> int:
        """
        :return: The volume number as an integer
        """
        try:
            if re.match(r"^p[0-9]+[ ]*v[0-9]+$", self.volume.lower()):
                return int(self.volume.lower().split("v")[1])
            else:
                stripped = ""
                for char in self.volume:
                    if char.isdigit() or char in [".", "-"]:
                        stripped += char
                if "-" in stripped:
                    stripped = stripped.split("-")[1]
                if "." in stripped:
                    stripped = stripped.split(".")[0]
                return int(stripped)

        except (TypeError, ValueError):
            return 0
