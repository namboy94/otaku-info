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

import math
import json
import requests
from typing import List, Dict, Any


def load_user_manga_list(username: str, custom_list: str) \
        -> List[Dict[str, Any]]:
    """
    Loads the manga anilist for a user
    :param username: The username
    :param custom_list: The custom list to load
    :return: The manga anilist
    """
    query = """
        query ($username: String) {
            MediaListCollection(userName: $username, type: MANGA) {
                lists {
                    name
                    entries {
                        progress
                        media {
                            id
                            chapters
                            title {
                                english
                                romaji
                            }
                        }
                    }
                }
            }
        }
        """
    user_lists = json.loads(requests.post(
        "https://graphql.anilist.co",
        json={"query": query, "variables": {"username": username}}
    ).text)["data"]["MediaListCollection"]["lists"]

    entries = []
    for _list in user_lists:
        if _list["name"] == custom_list:
            entries += _list["entries"]

    return entries


def load_user_anime_list(username: str, custom_list: str) \
        -> List[Dict[str, Any]]:
    """
    Loads the anime anilist for a user
    :param username: The username
    :param custom_list: The custom list to load
    :return: The anime anilist
    """
    query = """
        query ($username: String) {
            MediaListCollection(userName: $username, type: ANIME) {
                lists {
                    name
                    entries {
                        progress
                        media {
                            id
                            episodes
                            title {
                                english
                                romaji
                            }
                        }
                    }
                }
            }
        }
        """
    user_lists = json.loads(requests.post(
        "https://graphql.anilist.co",
        json={"query": query, "variables": {"username": username}}
    ).text)["data"]["MediaListCollection"]["lists"]

    entries = []
    for _list in user_lists:
        if _list["name"] == custom_list:
            entries += _list["entries"]

    return entries


def guess_latest_manga_chapter(anilist_id: int) -> int:
    """
    Guesses the latest chapter number based on anilist user activity
    :param anilist_id: The anilist ID to check
    :return: The latest chapter number
    """
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
    resp = requests.post(
        "https://graphql.anilist.co",
        json={"query": query, "variables": {"id": anilist_id}}
    )
    data = json.loads(resp.text)["data"]["Page"]["activities"]

    progresses = []
    for entry in data:
        progress = entry["progress"]
        if progress is not None:
            progress = entry["progress"].split(" - ")[-1]
            progresses.append(int(progress))

    progresses.sort(reverse=True)
    best_guess = progresses[0]

    if len(progresses) > 2:
        diff = progresses[0] - progresses[1]
        inverse_diff = 1 + math.ceil(50 / (diff + 1))
        if len(progresses) >= inverse_diff:
            if progresses[1] == progresses[inverse_diff]:
                best_guess = progresses[1]

    return best_guess
