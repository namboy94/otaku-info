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


from typing import Optional, List
from puffotter.graphql import GraphQlClient
from otaku_info_web.utils.enums import MediaType
from otaku_info_web.utils.anilist.AnilistListItem import AnilistListItem


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
        if progress is not None:
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
) -> List[AnilistListItem]:
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
                    media {
                        id
                        chapters
                        episodes
                        status
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
                    }
                }
            }
        }
    }
    """
    resp = graphql.query(query, {
        "username": username,
        "media_type": media_type.value.upper()
    })
    if resp is None:
        return []
    user_lists = resp["data"]["MediaListCollection"]["lists"]

    return [
        AnilistListItem(
            entry["media"]["anilist_id"],
            media_type,
            entry["media"]["title"]["english"],
            entry["media"]["title"]["romaji"],
            entry["media"]["coverImage"]["large"],
            entry["media"]["chapters"],
            entry["media"]["episodes"],
            entry["media"]["status"],
            entry["score"],
            entry["progress"],
            list_name
        ) for entry, list_name in [
            (y["entries"], y["name"]) for y in user_lists
        ]
    ]
