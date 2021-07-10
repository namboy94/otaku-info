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
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.enums import ListService, MediaType


class MediaListItem(ModelMixin, db.Model):
    """
    Database model for media list items.
    This model maps MediaLists and MediaUserStates
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "media_list_items"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ("user_state_service", "user_state_service_id",
             "user_state_media_type", "user_state_user_id"),
            (MediaUserState.service, MediaUserState.service_id,
             MediaUserState.media_type, MediaUserState.user_id)
        ),
        db.ForeignKeyConstraint(
            ("media_list_service", "media_list_media_type",
             "media_list_user_id", "media_list_name"),
            (MediaList.service, MediaList.media_type,
             MediaList.user_id, MediaList.name)
        )
    )

    user_state_service: ListService =\
        db.Column(db.Enum(ListService), primary_key=True)
    user_state_service_id: str = db.Column(db.String(255), primary_key=True)
    user_state_media_type: MediaType = \
        db.Column(db.Enum(MediaType), primary_key=True)
    user_state_user_id: int = db.Column(db.Integer, primary_key=True)

    media_list_service: ListService = \
        db.Column(db.Enum(ListService), primary_key=True)
    media_list_media_type: MediaType = \
        db.Column(db.Enum(MediaType), primary_key=True)
    media_list_user_id: int = db.Column(db.Integer, primary_key=True)
    media_list_name: int = db.Column(db.String(255), primary_key=True)

    user_state: MediaUserState = db.relationship(
        "MediaUserState", back_populates="media_list_items"
    )
    media_list: MediaList = db.relationship(
        "MediaList", back_populates="list_items"
    )
