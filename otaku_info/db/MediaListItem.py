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

from typing import Dict, Any
from puffotter.flask.base import db
from puffotter.flask.db.ModelMixin import ModelMixin
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaUserState import MediaUserState


class MediaListItem(ModelMixin, db.Model):
    """
    Database model for media list items.
    This model maps MediaLists and MediaUserStates
    """

    __tablename__ = "media_list_items"
    """
    The name of the database table
    """

    __table_args__ = (
        db.UniqueConstraint(
            "media_list_id",
            "media_user_state_id",
            name="unique_media_list_item"
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

    media_list_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_lists.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the media list this list item is a part of
    """

    media_list: MediaList = db.relationship(
        "MediaList",
        backref=db.backref("media_list_items", lazy=True, cascade="all,delete")
    )
    """
    The media list this list item is a part of
    """

    media_user_state_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_user_states.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the media user state this list item references
    """

    media_user_state: MediaUserState = db.relationship(
        "MediaUserState",
        backref=db.backref("media_list_items", lazy=True, cascade="all,delete")
    )
    """
    The media user state this list item references
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
            "media_list_id": self.media_list_id,
            "media_user_state_id": self.media_user_state_id
        }
        if include_children:
            data["media_list"] = self.media_list.__json__(include_children)
            data["media_user_state"] = \
                self.media_user_state.__json__(include_children)
        return data
