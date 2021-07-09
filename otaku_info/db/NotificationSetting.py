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
from jerrycan.db.User import User
from jerrycan.db.ModelMixin import ModelMixin
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
