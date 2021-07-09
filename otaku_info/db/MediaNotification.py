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
from jerrycan.db.ModelMixin import NoIDModelMixin
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.enums import ListService, MediaType


class MediaNotification(NoIDModelMixin, db.Model):
    """
    Database model that stores a media notification for a user
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "media_notifications"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ("service", "service_id", "media_type", "user_id"),
            (MediaUserState.service, MediaUserState.service_id,
             MediaUserState.media_type, MediaUserState.user_id)
        ),
    )

    service: ListService = db.Column(db.Enum(ListService), primary_key=True)
    service_id: str = db.Column(db.String(255), primary_key=True)
    media_type: MediaType = db.Column(db.Enum(MediaType), primary_key=True)
    user_id: int = db.Column(db.Integer, primary_key=True)

    last_update = db.Column(db.Integer, nullable=False)

    media_user_state: MediaUserState = db.relationship(
        "MediaUserState", back_populates="media_notification"
    )
