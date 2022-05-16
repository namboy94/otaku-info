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

import json
import time
import requests
from jerrycan.base import app
from typing import Optional, List, Dict, Any, Union
from otaku_info.external.entities.MangadexItem import MangadexItem


def fetch_all_mangadex_items() -> List[MangadexItem]:
    """
    Fetches all available mangadex items
    :return: The mangadex items
    """
    url = "https://api.mangadex.org/manga"
    items: List[Dict[str, Any]] = []
    mangadex_items: List[MangadexItem] = []
    page = 0
    last_date = "1970-01-01T00:00:00"

    while True:
        params: Dict[str, Union[int, str]] = {
            "createdAtSince": last_date,
            "order[createdAt]": "asc",
            "limit": 100,
            "offset": 100 * page
        }
        app.logger.debug(f"Mangadex: {params}")
        response = requests.get(url, params=params)
        data = json.loads(response.text)
        time.sleep(1)

        if data["result"] == "error":
            # TODO understand what's happening here
            new_date = items[-1]["attributes"]["createdAt"]
            new_date = new_date.split("T")[0] + "T00:00:00"

            if new_date == last_date:
                break
            else:
                last_date = new_date
                page = 0
                continue
        elif len(data["data"]) == 0:
            break

        items += data["data"]
        new_items = [
            MangadexItem.from_json(x)
            for x in data["data"]
        ]
        add_covers(new_items)
        mangadex_items += new_items
        page += 1

    mangadex_items.sort(key=lambda x: x.english_title)
    return mangadex_items


def fetch_mangadex_item(mangadex_id: str) -> Optional[MangadexItem]:
    """
    Fetches information for a mangadex
    """
    url = "https://api.mangadex.org/manga"
    response = requests.get(url, params={"ids[]": mangadex_id})
    time.sleep(1)

    if response.status_code >= 300:
        return None

    data = json.loads(response.text)["data"][0]
    return MangadexItem.from_json(data)


def add_covers(mangadex_items: List[MangadexItem]):
    """
    Adds cover URLs to mangadex items
    :param mangadex_items: The mangadex items
    :return: None
    """
    url = "https://api.mangadex.org/cover"
    ids = [
        x.cover_url
        for x in mangadex_items
        if x.cover_url is not None and len(x.cover_url) == 36
    ]
    params: Dict[str, Union[int, list]] = {"ids[]": [ids], "limit": 100}
    response = requests.get(url, params=params)
    data = json.loads(response.text)
    results = data["data"]
    time.sleep(1)

    covers = {}
    for result in results:
        relations = {x["type"]: x["id"] for x in result["relationships"]}
        covers[relations["manga"]] = result["attributes"]["fileName"]

    for mangadex_item in mangadex_items:
        filename = covers.get(mangadex_item.mangadex_id)
        if filename is None:
            mangadex_item.cover_url = ""
        else:
            mangadex_item.cover_url = f"https://uploads.mangadex.org/covers/" \
                                      f"{mangadex_item.mangadex_id}/{filename}"
