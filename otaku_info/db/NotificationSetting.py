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

from typing import Dict, Any, Tuple
from jerrycan.base import db
from jerrycan.db.User import User
from otaku_info.db.ModelMixin import ModelMixin
from otaku_info.enums import NotificationType


class NotificationSetting(ModelMixin, db.Model):
    """
    Database model that stores notification settings for a user
    """

    __tablename__ = "notification_settings"
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

    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the user associated with this notification setting
    """

    user: User = db.relationship(
        "User",
        backref=db.backref(
            "notification_settings", lazy=True, cascade="all,delete"
        )
    )
    """
    The user associated with this notification setting
    """

    notification_type: str = \
        db.Column(db.Enum(NotificationType), nullable=False)
    """
    The notification type
    """

    minimum_score: int = db.Column(db.Integer, default=0, nullable=False)
    """
    The minimum score for notification items
    """

    value: bool = db.Column(db.Boolean, nullable=False, default=False)
    """
    Whether or not the notification is active or not
    """

    @property
    def identifier_tuple(self) -> Tuple[int]:
        """
        :return: A tuple that uniquely identifies this database entry
        """
        return self.user_id,

    def update(self, new_data: "NotificationSetting"):
        """
        Updates the data in this record based on another object
        :param new_data: The object from which to use the new values
        :return: None
        """
        self.user_id = new_data.user_id
        self.notification_type = new_data.notification_type
        self.value = new_data.value
        self.minimum_score = new_data.minimum_score

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models
                                 will be included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "notification_type": self.notification_type,
            "value": self.value
        }
        if include_children:
            data["user"] = self.user.__json__(include_children)
        return data
