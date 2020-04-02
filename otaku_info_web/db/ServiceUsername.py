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
from otaku_info_web.utils.enums import ListService


class ServiceUsername(ModelMixin, db.Model):
    """
    Database model that stores an external service username for a user
    """

    __tablename__ = "service_usernames"
    """
    The name of the database table
    """

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "username",
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

    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the user associated with this service username
    """

    user: User = db.relationship(
        "User",
        backref=db.backref(
            "service_usernames", lazy=True, cascade="all,delete"
        )
    )
    """
    The user associated with this service username
    """

    username: str = db.Column(db.String(255), nullable=False)
    """
    The service username
    """

    service: ListService = db.Column(db.Enum(ListService), nullable=False)
    """
    The external service this item is a username for
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
            "user_id": self.user_id,
            "username": self.username,
            "service": self.service.value
        }
        if include_children:
            data["user"] = self.user.__json__(include_children)
        return data
