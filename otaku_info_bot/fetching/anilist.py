"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-bot.

otaku-info-bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-bot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import json
import requests
from typing import List, Dict, Any, Optional


def load_anilist(
        username: str,
        media_type: str,
        list_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Loads the anilist for a user
    :param username: The username
    :param media_type: The media type, either MANGA or ANIME
    :param list_name: Optionalyy restrict to a specific list
    :return: The anilist
    """
    graphql = GraphQlClient("https://graphql.anilist.co")
    query = """
    query ($username: String, $media_type: MediaType) {
        MediaListCollection(userName: $username, type: $media_type) {
            lists {
                name
                entries {
                    progress
                    media {
                        id
                        chapters
                        episodes
                        status
                        title {
                            english
                            romaji
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
        "media_type": media_type.upper()
    })
    if resp is None:
        return []
    user_lists = resp["data"]["MediaListCollection"]["lists"]

    entries = []  # type: List[Dict[str, Any]]
    for _list in user_lists:
        if list_name is None or _list["name"] == list_name:
            entries += _list["entries"]

    return entries


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

    progresses.sort(key=lambda x: progresses.count(x), reverse=True)
    progresses = sorted(progresses, key=progresses.count, reverse=True)
    best_guess = progresses[0]

    return best_guess


class GraphQlClient:
    """
    A simple API wrapper for GraphQL APIs
    """

    def __init__(self, api_url: str):
        """
        Initializes the GraphQL API wrapper
        :param api_url: The API endpoint URL
        """
        self.api_url = api_url

    def query(
            self,
            query_string: str,
            variables: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Executes a GraphQL query
        :param query_string: The query string to use
        :param variables: The variables to send
        :return: The response JSON, or None if an error occurred.
        """
        if variables is None:
            variables = {}

        resp = requests.post(self.api_url, json={
            "query": query_string,
            "variables": variables
        })
        if not resp.status_code < 300:
            return None
        else:
            return json.loads(resp.text)
