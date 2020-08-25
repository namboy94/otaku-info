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
from otaku_info.enums import MediaType, MediaSubType, \
    ReleasingState, ListService, MediaRelationType
from otaku_info.external.entities.AnimeListItem import AnimeListItem


class MyanimelistItem(AnimeListItem):
    """
    Class that models a general myanimelist list item
    Represents the information fetched using myanimelist's jikan API
    """

    @classmethod
    def from_query(cls, media_type: MediaType, data: Dict[str, Any]) \
            -> "MyanimelistItem":
        """
        Generates an MyanimelistItem from a dictionary generated
        by an APi query
        :param media_type: The media type of the item
        :param data: The data to use
        :return: The generated MyanimelistItem
        """
        media_subtype = cls.resolve_media_subtype(data["type"])
        releasing_state = cls.resolve_releasing_state(data["status"])

        relations = {}
        for edge_type, edges in data["related"].items():
            relation_type = cls.resolve_relation_type(edge_type)
            for edge in edges:
                node_type = MediaType(edge["type"])
                node_id = edge["mal_id"]
                relations[(node_type, node_id)] = relation_type

        return cls(
            data["mal_id"],
            ListService.MYANIMELIST,
            {},
            media_type,
            media_subtype,
            data["title_english"],
            data["title"],
            data["image_url"],
            data.get("chapters"),
            data.get("volumes"),
            data.get("episodes"),
            releasing_state,
            relations
        )

    @staticmethod
    def resolve_relation_type(relation_string: str) -> MediaRelationType:
        """
        Resolves myanimelist relation types
        :param relation_string: The string to resolve
        :return: The resolved MediaRelationType
        """
        base = {
            x.value.lower().replace("_", " "): x
            for x in MediaRelationType
        }
        base.update({
            "parent story": MediaRelationType.PARENT,
            "alternative setting": MediaRelationType.ALTERNATIVE
        })
        return base[relation_string.lower()]

    @staticmethod
    def resolve_releasing_state(releasing_string: str) -> ReleasingState:
        """
        Resolves myanimelist releasing state
        :param releasing_string: The string to resolve
        :return: The resolved ReleasingState
        """
        base = {
            x.value.lower().replace("_", " "): x
            for x in ReleasingState
        }
        base.update({
            "finished airing": ReleasingState.FINISHED,
            "publishing": ReleasingState.RELEASING,
            "airing": ReleasingState.RELEASING
        })
        return base[releasing_string.lower()]

    @staticmethod
    def resolve_media_subtype(subtype_string: str) -> MediaSubType:
        """
        Resolves myanimelist media subtype
        :param subtype_string: The string to resolve
        :return: The resolved MediaSubType
        """
        base = {
            x.value.lower().replace("_", " "): x
            for x in MediaSubType
        }
        base.update({
            "one-shot": MediaSubType.ONE_SHOT
        })
        return base[subtype_string.lower()]
