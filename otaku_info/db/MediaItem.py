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

from flask import url_for
from datetime import datetime
from typing import Dict, Optional, List, TYPE_CHECKING
from jerrycan.base import db
from jerrycan.db.ModelMixin import NoIDModelMixin
from otaku_info.db import MediaUserState, MangaChapterGuess
from otaku_info.enums import ReleasingState, MediaType, MediaSubType, \
    ListService
from otaku_info.utils.urls import generate_service_url, \
    generate_service_icon_url
if TYPE_CHECKING:
    from otaku_info.db.MediaIdMapping import MediaIdMapping
    from otaku_info.db.LnRelease import LnRelease


class MediaItem(NoIDModelMixin, db.Model):
    """
    Database model for media items.
    These model a representation of a series specific to one list service
    like anilist or mangadex.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "media_items"
    service: ListService = db.Column(db.Enum(ListService), primary_key=True)
    service_id: str = db.Column(db.String(255), primary_key=True)
    media_type: MediaType = db.Column(db.Enum(MediaType), primary_key=True)

    media_subtype: MediaSubType = \
        db.Column(db.Enum(MediaSubType), nullable=False)
    english_title: Optional[str] = db.Column(db.Unicode(255), nullable=True)
    romaji_title: str = db.Column(db.Unicode(255), nullable=False)
    cover_url: str = db.Column(db.String(255), nullable=False)
    latest_release: Optional[int] = db.Column(db.Integer, nullable=True)
    latest_volume_release: Optional[int] = db.Column(db.Integer, nullable=True)
    next_episode: Optional[int] = db.Column(db.Integer, nullable=True)
    next_episode_airing_time: Optional[int] = \
        db.Column(db.Integer, nullable=True)
    releasing_state: ReleasingState = \
        db.Column(db.Enum(ReleasingState), nullable=False)

    media_id_mappings: List["MediaIdMapping"] = db.relationship(
        "MediaIdMapping", back_populates="media_item", cascade="all, delete"
    )
    media_user_states: List["MediaUserState"] = db.relationship(
        "MediaUserState", back_populates="media_item", cascade="all, delete"
    )
    ln_releases: List["LnRelease"] = db.relationship(
        "LnRelease", back_populates="media_item", cascade="all, delete"
    )
    chapter_guess: Optional["MangaChapterGuess"] = db.relationship(
        "MangaChapterGuess",
        uselist=False,
        back_populates="media_id",
        cascade="all, delete"
    )

    @property
    def service_url(self) -> str:
        """
        :return: The URL to the series for the given service
        """
        return generate_service_url(
            self.service,
            self.media_type,
            self.service_id
        )

    @property
    def service_icon(self) -> str:
        """
        :return: The path to the service's icon file
        """
        return generate_service_icon_url(self.service)

    @property
    def current_release(self) -> Optional[int]:
        """
        The most current release, specifically tailored to the type of media
        :return: None
        """
        if self.next_episode is not None:
            return self.next_episode - 1
        elif self.latest_volume_release is not None:
            return self.latest_volume_release
        elif self.latest_release is not None:
            return self.latest_release
        else:
            return None

    @property
    def related_ids(self) -> Dict[ListService, str]:
        """
        :return: A dictionary mapping list services to IDs for this media item
        """
        return {
            x.secondary_media_item.service: x.secondary_media_item.service_id
            for x in self.media_id_mappings
        }

    @property
    def title(self) -> str:
        """
        :return: The default title for the media item.
        """
        if self.english_title is None:
            return self.romaji_title
        else:
            return self.english_title

    @property
    def own_url(self) -> str:
        """
        :return: The URL to the item's page on the otaku-info site
        """
        return url_for("media.media", media_item_id=self.id)

    @property
    def next_episode_datetime(self) -> Optional[datetime]:
        """
        :return: The datetime for when the next episode airs
        """
        if self.next_episode_airing_time is None:
            return None
        else:
            return datetime.fromtimestamp(self.next_episode_airing_time)
