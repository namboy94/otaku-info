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
from typing import Optional, List
from jerrycan.base import db
from jerrycan.db.ModelMixin import ModelMixin
from otaku_info.db.MediaItem import MediaItem


class LnRelease(ModelMixin, db.Model):
    """
    Database model that keeps track of light novel releases
    """

    __tablename__ = "ln_releases"
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

    media_item_id: int = db.Column(
        db.Integer, db.ForeignKey("media_items.id"), nullable=True
    )
    """
    The ID of the media item referenced by this release
    """

    media_item: MediaItem = db.relationship(
        "MediaItem",
        back_populates="ln_releases"
    )
    """
    The media item referenced by this release
    """

    release_date_string: str = db.Column(db.String(10), nullable=False)
    """
    The release date as a ISO-8601 string
    """

    series_name: str = db.Column(db.String(255), nullable=False)
    """
    The series name
    """

    volume: str = db.Column(db.String(255), nullable=False)
    """
    The volume identifier
    """

    publisher: Optional[str] = db.Column(db.String(255), nullable=True)
    """
    The publisher
    """

    purchase_link: Optional[str] = db.Column(db.String(255), nullable=True)
    """
    Link to a store page
    """

    digital: bool = db.Column(db.Boolean)
    """
    Whether this is a digital release
    """

    physical: bool = db.Column(db.Boolean)
    """
    Whether this is a physical release
    """

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
