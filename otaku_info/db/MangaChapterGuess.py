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
from jerrycan.base import db
from jerrycan.db.ModelMixin import NoIDModelMixin
from otaku_info.db.MediaItem import MediaItem
from otaku_info.enums import MediaType, ListService
from otaku_info.external.anilist import guess_latest_manga_chapter


class MangaChapterGuess(NoIDModelMixin, db.Model):
    """
    Database model that keeps track of manga chapter guesses.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "manga_chapter_guesses"
    __table_args__ = (db.ForeignKeyConstraint(
        ("service", "service_id", "media_type"),
        (MediaItem.service, MediaItem.service_id, MediaItem.media_type)
    ),)

    service: ListService = db.Column(db.Enum(ListService), primary_key=True)
    service_id: str = db.Column(db.String(255), primary_key=True)
    media_type: MediaType = db.Column(db.Enum(MediaType), primary_key=True)

    guess: int = db.Column(db.Integer, nullable=True)
    last_update: int = db.Column(db.Integer, nullable=False, default=0)

    media_item: MediaItem = db.relationship(
        "MediaItem", back_populates="media_user_states"
    )

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
