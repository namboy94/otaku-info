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

from typing import Dict, Any, Optional
from puffotter.flask.base import db
from puffotter.flask.db.ModelMixin import ModelMixin
from otaku_info.utils.db_model_helper import build_title
from otaku_info.utils.enums import ReleasingState, MediaType, MediaSubType


class MediaItem(ModelMixin, db.Model):
    """
    Database model for media items.
    These model a generic, site-agnostic representation of a series.
    """

    __tablename__ = "media_items"
    """
    The name of the database table
    """

    __table_args__ = (
        db.UniqueConstraint(
            "media_type",
            "media_subtype",
            "romaji_title",
            "cover_url",
            name="unique_media_item"
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

    media_type: MediaType = db.Column(db.Enum(MediaType), nullable=False)
    """
    The media type of the list item
    """

    media_subtype: MediaSubType = db.Column(
        db.Enum(MediaSubType), nullable=False
    )
    """
    The subtype (for example, TV short, movie oneshot etc)
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

    releasing_state: ReleasingState = db.Column(
        db.Enum(ReleasingState), nullable=False
    )
    """
    The current releasing state of the media item
    """

    @property
    def title(self) -> str:
        """
        :return: The default title for the media item.
        """
        return build_title(self.english_title, self.romaji_title)

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models
                                 will be included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "media_type": self.media_type.value,
            "media_subtype": self.media_subtype.value,
            "english_title": self.english_title,
            "romaji_title": self.romaji_title,
            "cover_url": self.cover_url,
            "latest_release": self.latest_release,
            "releasing_state": self.releasing_state.value
        }
        return data
