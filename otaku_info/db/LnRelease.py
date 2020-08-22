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

from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from puffotter.flask.base import db
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaId import MediaId
from otaku_info.db.ModelMixin import ModelMixin


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

    media_item_id: Optional[int] = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_items.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=True,
        unique=False
    )
    """
    The ID of the media item referenced by this light novel release
    """

    media_item: Optional[MediaItem] = db.relationship(
        "MediaItem",
        backref=db.backref(
            "ln_releases", lazy=True, cascade="all,delete"
        )
    )
    """
    The media item referenced by this light novel release
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
    def identifier_tuple(self) -> Tuple[int, str, bool, bool]:
        """
        :return: A tuple that uniquely identifies this database entry
        """
        return self.media_item_id, self.volume, self.digital, self.physical

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
            "release_date_string": self.release_date_string,
            "series_name": self.series_name,
            "volume": self.volume,
            "publisher": self.publisher,
            "purchase_link": self.purchase_link,
            "digital": self.digital,
            "physical": self.physical
        }
        if include_children:
            if self.media_item is None:
                data["media_item"] = None
            else:
                data["media_item"] = self.media_item.__json__(include_children)
        return data

    def get_ids(self) -> List[MediaId]:
        """
        :return: Any related Media IDs
        """
        if self.media_item is None:
            return []
        else:
            return MediaId.query.filter_by(media_item=self.media_item).all()
