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


class AnilistUserEntry(ModelMixin, db.Model):
    """
    Model that describes the 'anilist_user_entries' database table.
    This stores anilist data for a particular user
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "anilist_user_entries"
    """
    The name of the table
    """

    user_id = db.Column(
        db.Integer, db.ForeignKey(
            "users.id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the user associated with this user entry
    """

    user = db.relationship("User", backref=db.backref(
        "anilist_user_entries", lazy=True, cascade="all,delete"
    ))
    """
    The user associated with this user entry
    """

    entry_id = db.Column(
        db.Integer, db.ForeignKey(
            "anilist_entries.id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    The media entry of the user associated with this user entry
    """

    entry = db.relationship("AnilistEntry", backref=db.backref(
        "anilist_user_entries", lazy=True, cascade="all,delete"
    ))
    """
    The media entry associated with this user entry
    """

    progress = db.Column(db.Integer, default=0, nullable=False)
    """
    The chapter/episode progress of the user
    """

    score = db.Column(db.Integer, nullable=True)
    """
    The score the user gave the series
    """

    @property
    def diff(self) -> int:
        if self.entry.latest_chapter < self.progress:
            return 0
        else:
            return self.entry.latest_chapter - self.progress

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models will be
                                 included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "entry_id": self.entry_id,
            "progress": self.progress,
            "score": self.score
        }
        if include_children:
            data["user"] = self.user.__json__(include_children)
            data["entry"] = self.entry.__json__(include_children)
        return data
