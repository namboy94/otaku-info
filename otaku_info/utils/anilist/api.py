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

from typing import Optional, List
from puffotter.graphql import GraphQlClient
from otaku_info.utils.enums import MediaType
from otaku_info.utils.anilist.AnilistItem \
    import AnilistItem, AnilistUserItem


MEDIA_QUERY = """
    id
    chapters
    episodes
    status
    format
    title {
        english
        romaji
    }
    coverImage {
        large
    }
    nextAiringEpisode {
      episode
    }
    relations {
        edges {
            node {
                id
                type
            }
            relationType
        }
    }
"""


def guess_latest_manga_chapter(anilist_id: int) -> Optional[int]:
    """
    Guesses the latest chapter number based on anilist user activity
    :param anilist_id: The anilist ID to check
    :return: The latest chapter number
    """
    graphql = GraphQlClient("https://graphql.anilist.co")
    query = """
    query ($id: Int) {
        Page(page: 1) {
        activities(mediaId: $id, sort: ID_DESC) {
                ... on ListActivity {
                    progress
                    userId
                    status
                    media {
                        chapters
                    }
                }
            }
        }
    }
    """
    resp = graphql.query(query, {"id": anilist_id})
    if resp is None:
        return None

    data = resp["data"]["Page"]["activities"]

    progresses = []
    for entry in data:
        progress = entry["progress"]
        status = entry["status"]
        chapters = entry["media"]["chapters"]

        if status == "completed":
            progresses.append(chapters)
        elif progress is not None:
            progress = entry["progress"].split(" - ")[-1]
            progresses.append(int(progress))

    progresses = progresses[0:20]
    progresses.sort(key=lambda x: progresses.count(x), reverse=True)
    progresses = sorted(progresses, key=progresses.count, reverse=True)

    try:
        return progresses[0]
    except IndexError:
        return None


def load_anilist(
        username: str,
        media_type: MediaType
) -> List[AnilistUserItem]:
    """
    Loads the anilist for a user
    :param username: The username
    :param media_type: The media type, either MANGA or ANIME
    :return: The anilist list items for the user and media type
    """
    graphql = GraphQlClient("https://graphql.anilist.co")
    query = """
    query ($username: String, $media_type: MediaType) {
        MediaListCollection(userName: $username, type: $media_type) {
            lists {
                name
                entries {
                    progress
                    score
                    status
                    media {@{MEDIA_QUERY}}
                }
            }
        }
    }
    """.replace("@{MEDIA_QUERY}", MEDIA_QUERY)
    resp = graphql.query(query, {
        "username": username,
        "media_type": media_type.value.upper()
    })
    if resp is None:
        return []
    user_lists = resp["data"]["MediaListCollection"]["lists"]

    anilist_items: List[AnilistUserItem] = []
    for entries, list_name in [
        (y["entries"], y["name"]) for y in user_lists
    ]:
        for entry in entries:
            entry["list_name"] = list_name
            anilist_items.append(AnilistUserItem.from_query(media_type, entry))

    return anilist_items


def load_media_info(anilist_id: int, media_type: MediaType) \
        -> Optional[AnilistItem]:
    """
    Loads information for a single anilist media item
    :param anilist_id: The anilist media ID
    :param media_type: The media type
    :return: The fetched AnilistItem
    """
    graphql = GraphQlClient("https://graphql.anilist.co")
    query = """
        query ($id: Int, $media_type: MediaType) {
            Media(id: $id, type: $media_type) {
                @{MEDIA_QUERY}
            }
        }
    """.replace("@{MEDIA_QUERY}", MEDIA_QUERY)
    resp = graphql.query(
        query,
        {"id": anilist_id, "media_type": media_type.value.upper()}
    )
    if resp is None:
        return None
    else:
        return AnilistItem.from_query(media_type, resp["data"]["Media"])


def map_myanimelist_id_to_anilist_id(
        myanimelist_id: int,
        media_type: MediaType
) -> Optional[int]:
    """
    Translates a myanimelist ID to an Anilist ID
    :param myanimelist_id: The myanimelist ID
    :param media_type: The media type
    :return: The anilist ID
    """
    graphql = GraphQlClient("https://graphql.anilist.co")
    query = """
        query ($mal_id: Int, $type: MediaType) {
            Media(idMal: $mal_id, type: $type) {
                id
            }
        }
    """
    resp = graphql.query(
        query,
        {"mal_id": myanimelist_id, "media_type": media_type.value.upper()}
    )
    if resp is None:
        return None
    else:
        return int(resp["data"]["Media"]["id"])
