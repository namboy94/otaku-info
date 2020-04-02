"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-web.

otaku-info-web is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-web is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-web.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import Dict, Any
from puffotter.flask.base import db
from puffotter.flask.db.User import User
from puffotter.flask.db.ModelMixin import ModelMixin
from otaku_info_web.utils.enums import ListService, MediaType


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

    name: str = db.Column(db.String(255), nullable=False)
    """
    The name of this list
    """

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

    service: ListService = db.Column(db.Enum(ListService), nullable=False)
    """
    The service for which this list applies to
    """

    media_type: MediaType = db.Column(db.Enum(MediaType), nullable=False)
    """
    The media type for this list
    """

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
