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

from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING
from jerrycan.base import db
from jerrycan.db.User import User
from otaku_info.db.ModelMixin import ModelMixin
from otaku_info.db.MediaId import MediaId
from otaku_info.enums import ConsumingState
if TYPE_CHECKING:
    from otaku_info.db.MediaNotification import MediaNotification


class MediaUserState(ModelMixin, db.Model):
    """
    Database model that keeps track of a user's entries on external services
    for a media item
    """

    __tablename__ = "media_user_states"
    """
    The name of the database table
    """

    __table_args__ = (
        db.UniqueConstraint(
            "media_id_id",
            "user_id",
            name="unique_media_user_state"
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

    media_id_id: int = db.Column(
        db.Integer,
        db.ForeignKey("media_ids.id"),
        nullable=False
    )
    """
    The ID of the media ID referenced by this user state
    """

    media_id: MediaId = db.relationship(
        "MediaId",
        back_populates="media_user_states"
    )
    """
    The media ID referenced by this user state
    """

    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the user associated with this user state
    """

    user: User = db.relationship(
        "User",
        backref=db.backref(
            "media_user_states", lazy=True, cascade="all,delete"
        )
    )
    """
    The user associated with this user state
    """

    progress: Optional[int] = db.Column(db.Integer, nullable=True)
    """
    The user's current progress consuming the media item
    """

    volume_progress: Optional[int] = db.Column(db.Integer, nullable=True)
    """
    The user's current 'volume' progress.
    """

    score: Optional[int] = db.Column(db.Integer, nullable=True)
    """
    The user's score for the references media item
    """

    consuming_state: ConsumingState \
        = db.Column(db.Enum(ConsumingState), nullable=False)
    """
    The current consuming state of the user for this media item
    """

    media_notification: Optional["MediaNotification"] = db.relationship(
        "MediaNotification",
        uselist=False,
        back_populates="media_user_state",
        cascade="all, delete"
    )
    """
    Notification object for this user state
    """

    @property
    def identifier_tuple(self) -> Tuple[int, int]:
        """
        :return: A tuple that uniquely identifies this database entry
        """
        return self.media_id_id, self.user_id

    def update(self, new_data: "MediaUserState"):
        """
        Updates the data in this record based on another object
        :param new_data: The object from which to use the new values
        :return: None
        """
        self.media_id_id = new_data.media_id_id
        self.user_id = new_data.user_id
        self.progress = new_data.progress
        self.volume_progress = new_data.volume_progress
        self.score = new_data.score
        self.consuming_state = new_data.consuming_state
