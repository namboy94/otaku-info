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
from jerrycan.db.ModelMixin import ModelMixin
from otaku_info.db.MediaUserState import MediaUserState


class MediaNotification(ModelMixin, db.Model):
    """
    Database model that stores a media notification for a user
    """

    __tablename__ = "media_notifications"
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

    media_user_state_id: int = db.Column(
        db.Integer,
        db.ForeignKey("media_user_states.id"),
        nullable=False,
        unique=True
    )
    """
    The ID of the media user state this notification references
    """

    media_user_state: MediaUserState = db.relationship(
        "MediaUserState", back_populates="media_notification"
    )
    """
    The media user state this notification references
    """

    last_update = db.Column(db.Integer, nullable=False)
    """
    The last update value sent to the user
    """
