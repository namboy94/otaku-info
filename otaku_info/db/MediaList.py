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

from typing import Dict, Any, List, TYPE_CHECKING, Tuple
from puffotter.flask.base import db
from puffotter.flask.db.User import User
from otaku_info.db.ModelMixin import ModelMixin
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

    @property
    def identifier_tuple(self) -> Tuple[str, int, ListService, MediaType]:
        """
        :return: A tuple that uniquely identifies this database entry
        """
        return self.name, self.user_id, self.service, self.media_type

    def update(self, new_data: "MediaList"):
        """
        Updates the data in this record based on another object
        :param new_data: The object from which to use the new values
        :return: None
        """
        self.user_id = new_data.user_id
        self.name = new_data.name
        self.service = new_data.service
        self.media_type = new_data.media_type

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models
                                 will be included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "service": self.service.value,
            "media_type": self.media_type.value
        }
        if include_children:
            data["user"] = self.user.__json__(include_children)
        return data
