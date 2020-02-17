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

import time
from typing import Dict, Any
from otaku_info_web.flask import db, app
from otaku_info_web.enums import MediaType, ReleaseState
from otaku_info_web.db.ModelMixin import ModelMixin
from otaku_info_web.data.anilist import guess_latest_manga_chapter


class AnilistEntry(ModelMixin, db.Model):
    """
    Model that describes the 'anilist_entries' database table.
    This stores anilist data in the database to avoid querying
    anilist for every anilist-related request
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "anilist_entries"
    """
    The name of the table
    """

    anilist_id = db.Column(db.Integer, nullable=False)
    """
    The anilist ID of the entry
    """

    romaji_name = db.Column(db.String(255), nullable=False)
    """
    The name of the series in Romaji
    """

    english_name = db.Column(db.String(255), nullable=True)
    """
    The name of the series in English
    """

    media_type = db.Column(db.Enum(MediaType), nullable=False)
    """
    The media type of the entry
    """

    release_state = db.Column(db.Enum(ReleaseState), nullable=False)
    """
    The releasing state of the entry
    """

    latest = db.Column(db.Integer, nullable=True)
    """
    The most recently released episode/chapter. Can be None if this is
    unknown (as is often the case with manga)
    """

    chapter_guess = db.Column(db.Integer, nullable=True)
    """
    Best guess of the latest manga chapter using anilist's community features
    """

    last_chapter_guess_check = db.Column(db.Integer, default=0, nullable=False)
    """
    Last time the chapter guess was updated as a unix timestamp
    """

    image_url = db.Column(db.String(255), nullable=False)
    """
    URL to the series' cover art image
    """
    # TODO CHECK IF IMAGE EXISTS

    @property
    def latest_chapter(self) -> int:
        """
        :return: The latest chapter (or at least a good guess)
        """
        if self.release_state == ReleaseState.FINISHED:
            latest = self.latest
        else:
            latest = self.chapter_guess
        return 0 if latest is None else latest

    @property
    def name(self) -> str:
        """
        :return: The name of the series, with priority given
                 to the English name
        """
        if self.english_name is None:
            return self.romaji_name
        else:
            return self.english_name

    @property
    def anilist_url(self) -> str:
        """
        :return: The URL to the anilist page
        """
        return "https://anilist.co/{}/{}".format(
            self.media_type.value, self.anilist_id
        )

    def update_chapter_guess(self):
        """
        Updates the chapter guess
        :return: None
        """
        if self.last_chapter_guess_check:
            print(time.time() - self.last_chapter_guess_check)
        if self.media_type == MediaType.MANGA:
            app.logger.debug("Checking chapter guess for {}".format(self.name))
        if self.media_type == MediaType.MANGA \
                and self.release_state == ReleaseState.RELEASING \
                and time.time() - self.last_chapter_guess_check > 3600:
            app.logger.info("Updating chapter guess")
            self.chapter_guess = guess_latest_manga_chapter(self.anilist_id)
            self.last_chapter_guess_check = time.time()

    def update(self, update_data: Dict[str, Any], media_type: MediaType):
        """
        Updates the values based on data from anilist
        :param update_data: The anilist data
        :param media_type: The media type
        :return: None
        """
        self.anilist_id = update_data["id"]
        self.media_type = media_type

        self.release_state = ReleaseState(update_data["status"].lower())
        self.english_name = update_data["title"]["english"]
        self.romaji_name = update_data["title"]["romaji"]
        self.image_url = update_data["coverImage"]["large"] \
            .replace("medium", "large")

        keyword = "chapters" \
            if self.media_type == MediaType.MANGA \
            else "episodes"

        if self.release_state == ReleaseState.FINISHED:
            latest = update_data[keyword]
        elif media_type == MediaType.ANIME:
            latest_ep = None
            next_ep = update_data["nextAiringEpisode"]
            if next_ep is not None:
                latest_ep = next_ep["episode"] - 1
            latest = latest_ep
        else:
            latest = None

        self.latest = latest

    @classmethod
    def from_data(cls, anilist_data: Dict[str, Any], media_type: MediaType):
        """
        Generates a new entry from anilist data
        :param anilist_data: The anilist data
        :param media_type: The media type
        :return: The generated entry
        """
        entry = cls()
        entry.update(anilist_data, media_type)
        return entry

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models will be
                                 included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        return {
            "id": self.id,
            "anilist_id": self.anilist_id,
            "romaji_name": self.romaji_name,
            "english_name": self.english_name,
            "media_type": self.media_type.value,
            "release_state": self.release_state.value,
            "latest": self.latest,
            "image_url": self.image_url,
            "chapter_guess": self.chapter_guess
        }
