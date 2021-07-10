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

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "media_lists"

    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        primary_key=True
    )
    name: str = db.Column(db.Unicode(255), primary_key=True)
    service: ListService = db.Column(db.Enum(ListService), primary_key=True)
    media_type: MediaType = db.Column(db.Enum(MediaType), primary_key=True)

    user: User = db.relationship(
        "User",
        backref=db.backref("media_lists", lazy=True, cascade="all, delete")
    )
    list_items: List["MediaListItem"] = db.relationship(
        "MediaListItem", back_populates="media_list", cascade="all, delete"
    )
