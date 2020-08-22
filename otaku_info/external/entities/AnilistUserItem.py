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

from typing import Optional, Dict, Any, Tuple
from otaku_info.external.entities.AnilistItem import AnilistItem
from otaku_info.enums import MediaType, MediaSubType, \
    ReleasingState, ConsumingState, MediaRelationType


class AnilistUserItem(AnilistItem):
    """
    Class that models an anilist list item for a user
    Represents the information fetched using anilist's API
    """
    def __init__(
            self,
            anilist_id: int,
            myanimelist_id: Optional[int],
            media_type: MediaType,
            media_subtype: MediaSubType,
            english_title: Optional[str],
            romaji_title: str,
            cover_url: str,
            chapters: Optional[int],
            volumes: Optional[int],
            episodes: Optional[int],
            releasing_state: ReleasingState,
            relations: Dict[Tuple[MediaType, int], MediaRelationType],
            score: Optional[int],
            progress: Optional[int],
            consuming_state: ConsumingState,
            list_name: str
    ):
        """
        Initializes the AnilistItem object
        :param anilist_id: The anilist ID of the series
        :param myanimelist_id: The myanimelist ID of the series
        :param media_type: The media type of the series
        :param media_subtype: The media subtype of the series
        :param english_title: The English title of the series
        :param romaji_title: The Japanes title of the series written in romaji
        :param cover_url: URL to a cover image for the series
        :param chapters: The total amount of known manga chapters
        :param volumes: The total amount of known manga/ln volumes
        :param episodes: The total amount of known anime episodes
        :param releasing_state: The current releasing state of the series
        :param relations: Related media items identified by IDs
        :param score: The user's score for the series
        :param progress: The user's progress for the series
        :param consuming_state: The user's consumption state for the series
        :param list_name: Which of the user's lists this entry belongs to
        """
        super().__init__(
            anilist_id,
            myanimelist_id,
            media_type,
            media_subtype,
            english_title,
            romaji_title,
            cover_url,
            chapters,
            volumes,
            episodes,
            releasing_state,
            relations
        )
        self.score = score
        self.progress = progress
        self.consuming_state = consuming_state
        self.list_name = list_name

    @classmethod
    def from_query(
            cls,
            media_type: MediaType,
            data: Dict[str, Any]
    ) -> "AnilistUserItem":
        """
        Generates an AnilistUserItem from a dictionary generated
        by an APi query
        :param media_type: The media type of the item
        :param data: The data to use
        :return: The generated AnilistItem
        """
        base = AnilistItem.from_query(media_type, data["media"])
        consuming_state = ConsumingState(data["status"].lower())

        return AnilistUserItem(
            base.anilist_id,
            base.myanimelist_id,
            base.media_type,
            base.media_subtype,
            base.english_title,
            base.romaji_title,
            base.cover_url,
            base.chapters,
            base.volumes,
            base.episodes,
            base.releasing_state,
            base.relations,
            data["score"],
            data["progress"],
            consuming_state,
            data["list_name"]
        )
