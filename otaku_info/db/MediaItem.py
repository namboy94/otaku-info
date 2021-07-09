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
from typing import Dict, Optional, List, Tuple, TYPE_CHECKING
from jerrycan.base import db
from otaku_info.db.ModelMixin import ModelMixin
from otaku_info.enums import ReleasingState, MediaType, MediaSubType, \
    ListService
if TYPE_CHECKING:
    from otaku_info.db.MediaId import MediaId
    from otaku_info.db.LnRelease import LnRelease


class MediaItem(ModelMixin, db.Model):
    """
    Database model for media items.
    These model a representation of a series specific to one list service
    like anilist or mangadex.
    """

    __tablename__ = "media_items"
    """
    The name of the database table
    """

    __table_args__ = (
        db.UniqueConstraint(
            "service"
            "media_type",
            "service_id",
            name="unique_media_item"
        )
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

    service: ListService = db.Column(db.Enum(ListService), nullable=False)
    """
    The List service this media item is for
    """

    media_type: MediaType = db.Column(db.Enum(MediaType), nullable=False)
    """
    The media type of the list item
    """

    service_id: str = db.Column(db.String(255), nullable=False)
    """
    The Service ID on the list service
    """

    media_subtype: MediaSubType = db.Column(
        db.Enum(MediaSubType), nullable=False
    )
    """
    The media subtype (for example, TV short, movie oneshot etc)
    """

    english_title: Optional[str] = db.Column(db.Unicode(255), nullable=True)
    """
    The English title of the media item
    """

    romaji_title: str = db.Column(db.Unicode(255), nullable=False)
    """
    The Japanese title of the media item written in Romaji
    """

    cover_url: str = db.Column(db.String(255), nullable=False)
    """
    An URL to a cover image of the media item
    """

    latest_release: Optional[int] = db.Column(db.Integer, nullable=True)
    """
    The latest release chapter/episode for this media item
    """

    latest_volume_release: Optional[int] = db.Column(db.Integer, nullable=True)
    """
    The latest volume for this media item
    """

    next_episode: Optional[int] = db.Column(db.Integer, nullable=True)
    """
    The next episode to air
    """

    next_episode_airing_time: Optional[int] = \
        db.Column(db.Integer, nullable=True)
    """
    The time the next episode airs
    """

    releasing_state: ReleasingState = db.Column(
        db.Enum(ReleasingState), nullable=False
    )
    """
    The current releasing state of the media item
    """

    media_ids: List["MediaId"] = db.relationship(
        "MediaId", back_populates="media_item", cascade="all, delete"
    )
    """
    Media IDs associated with this Media item
    """

    ln_releases: List["LnRelease"] = db.relationship(
        "LnRelease", back_populates="media_item", cascade="all, delete"
    )
    """
    Light novel releases associated with this Media item
    """

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
    def media_id_mapping(self) -> Dict[ListService, "MediaId"]:
        """
        :return: A dictionary mapping list services to IDs for this media item
        """
        return {
            x.service: x for x in self.media_ids
        }

    @property
    def identifier_tuple(self) -> Tuple[ListService, MediaType, str]:
        """
        :return: A tuple that uniquely identifies this database entry
        """
        return self.service, self.media_type, self.service_id

    def update(self, new_data: "MediaItem"):
        """
        Updates the data in this record based on another object
        :param new_data: The object from which to use the new values
        :return: None
        """
        self.media_type = new_data.media_type
        self.media_subtype = new_data.media_subtype
        self.english_title = new_data.english_title
        self.romaji_title = new_data.romaji_title
        self.cover_url = new_data.cover_url
        self.latest_release = new_data.latest_release
        self.latest_volume_release = new_data.latest_volume_release
        self.releasing_state = new_data.releasing_state
        self.next_episode = new_data.next_episode
        self.next_episode_airing_time = new_data.next_episode_airing_time

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
