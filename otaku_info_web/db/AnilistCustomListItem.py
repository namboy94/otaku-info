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
from otaku_info_web.flask import db
from otaku_info_web.db.ModelMixin import ModelMixin


class AnilistCustomListItem(ModelMixin, db.Model):
    """
    Model that maps AnilistUserEntry items to AnilistCustomList items.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "anilist_custom_list_items"
    """
    The name of the table
    """

    custom_list_id = db.Column(
        db.Integer, db.ForeignKey(
            "anilist_custom_lists.id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the user associated with this user entry
    """

    custom_list = db.relationship("AnilistCustomList", backref=db.backref(
        "anilist_custom_list_items", lazy=True, cascade="all,delete"
    ))
    """
    The user associated with this user entry
    """

    user_entry_id = db.Column(
        db.Integer, db.ForeignKey(
            "anilist_user_entries.id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the media entry of the user associated with this item
    """

    user_entry = db.relationship("AnilistUserEntry", backref=db.backref(
        "anilist_custom_list_items", lazy=True, cascade="all,delete"
    ))
    """
    The media entry of the user associated with this item
    """

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models will be
                                 included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "custom_list_id": self.custom_list_id,
            "user_entry_id": self.user_entry_id
        }
        if include_children:
            data["custom_list"] = self.custom_list.__json__(include_children)
            data["user_entry"] = self.user_entry.__json__(include_children)
        return data
