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

from typing import List, TYPE_CHECKING
from jerrycan.base import db
from jerrycan.db.User import User
from jerrycan.db.ModelMixin import ModelMixin
from otaku_info.enums import ListService, MediaType
if TYPE_CHECKING:
    from otaku_info.db.MediaListItem import MediaListItem


class MediaList(ModelMixin, db.Model):
    """
    Database model for user-specific media lists.
    """

    __tablename__ = "media_lists"
    """
    The name of the database table
    """

    __table_args__ = (
        db.UniqueConstraint(
            "name",
            "user_id",
            "service",
            "media_type",
            name="unique_media_list"
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

    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the user associated with this list
    """

    user: User = db.relationship(
        "User",
        backref=db.backref("media_lists", lazy=True, cascade="all,delete")
    )
    """
    The user associated with this list
    """

    name: str = db.Column(db.Unicode(255), nullable=False)
    """
    The name of this list
    """

    service: ListService = db.Column(db.Enum(ListService), nullable=False)
    """
    The service for which this list applies to
    """

    media_type: MediaType = db.Column(db.Enum(MediaType), nullable=False)
    """
    The media type for this list
    """

    media_list_items: List["MediaListItem"] = db.relationship(
        "MediaListItem", back_populates="media_list", cascade="all, delete"
    )
    """
    Media List Items that are a part of this media list
    """
