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

import time
from typing import Dict, Any, Tuple
from puffotter.flask.base import db
from otaku_info.db.ModelMixin import ModelMixin
from otaku_info.db.MediaId import MediaId
from otaku_info.external.anilist import guess_latest_manga_chapter


class MangaChapterGuess(ModelMixin, db.Model):
    """
    Database model that keeps track of manga chapter guesses.
    """

    __tablename__ = "manga_chapter_guesses"
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

    media_id_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "media_ids.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        unique=True
    )
    """
    The ID of the media ID referenced by this manga chapter guess
    """

    media_id: MediaId = db.relationship(
        "MediaId",
        backref=db.backref(
            "manga_chapter_guesses", lazy=True, cascade="all,delete"
        )
    )
    """
    The media ID referenced by this manga chapter guess
    """

    guess: int = db.Column(db.Integer, nullable=True)
    """
    The actual guess for the most current chapter of the manga series
    """

    last_update: int = db.Column(db.Integer, nullable=False, default=0)
    """
    Timestamp from when the guess was last updated
    """

    def update_guess(self):
        """
        Updates the manga chapter guess
        (if the latest guess is older than an hour)
        :return: None
        """
        delta = time.time() - self.last_update
        if delta > 60 * 60:
            self.last_update = int(time.time())
            self.guess = guess_latest_manga_chapter(
                int(self.media_id.service_id)
            )

    @property
    def identifier_tuple(self) -> Tuple[int]:
        """
        :return: A tuple that uniquely identifies this database entry
        """
        return self.media_id_id,

    def update(self, new_data: "MangaChapterGuess"):
        """
        Updates the data in this record based on another object
        :param new_data: The object from which to use the new values
        :return: None
        """
        self.media_id_id = new_data.media_id_id
        self.guess = new_data.guess
        self.last_update = new_data.last_update

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models
                                 will be included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "media_id_id": self.media_id_id,
            "guess": self.guess,
            "last_update": self.last_update
        }
        if include_children:
            data["media_id"] = self.media_id.__json__(include_children)
        return data
