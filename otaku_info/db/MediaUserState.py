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

from typing import Optional, TYPE_CHECKING, List
from jerrycan.base import db
from jerrycan.db.User import User
from jerrycan.db.ModelMixin import NoIDModelMixin
from otaku_info.db.MediaItem import MediaItem
from otaku_info.enums import ConsumingState, ListService, MediaType
if TYPE_CHECKING:
    from otaku_info.db.MediaNotification import MediaNotification
    from otaku_info.db import MediaListItem


class MediaUserState(NoIDModelMixin, db.Model):
    """
    Database model that keeps track of a user's entries on external services
    for a media item
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "media_user_states"
    __table_args__ = (db.ForeignKeyConstraint(
        ("service", "service_id", "media_type"),
        (MediaItem.service, MediaItem.service_id, MediaItem.media_type)
    ),)

    service: ListService = db.Column(db.Enum(ListService), primary_key=True)
    service_id: str = db.Column(db.String(255), primary_key=True)
    media_type: MediaType = db.Column(db.Enum(MediaType), primary_key=True)
    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        primary_key=True
    )

    progress: Optional[int] = db.Column(db.Integer, nullable=True)
    volume_progress: Optional[int] = db.Column(db.Integer, nullable=True)
    score: Optional[int] = db.Column(db.Integer, nullable=True)
    consuming_state: ConsumingState \
        = db.Column(db.Enum(ConsumingState), nullable=False)

    media_item: MediaItem = db.relationship(
        "MediaItem", back_populates="media_user_states"
    )
    user: User = db.relationship(
        "User",
        backref=db.backref(
            "media_user_states", lazy=True, cascade="all,delete"
        )
    )
    media_notification: Optional["MediaNotification"] = db.relationship(
        "MediaNotification",
        uselist=False,
        back_populates="media_user_state",
        cascade="all, delete"
    )
    media_list_items: List["MediaListItem"] = db.relationship(
        "MediaListItem", back_populates="user_state", cascade="all, delete"
    )
