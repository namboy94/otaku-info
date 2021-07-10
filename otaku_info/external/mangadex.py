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
    mangadex_items = []
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

        if "results" not in data:
            new_date = items[-1]["data"]["attributes"]["createdAt"]
            new_date = new_date.split("T")[0] + "T00:00:00"

            if new_date == last_date:
                break
            else:
                last_date = new_date
                page = 0
                continue
        elif len(data["results"]) == 0:
            break

        items += data["results"]
        mangadex_items += [
            MangadexItem.from_json(x["data"])
            for x in data["results"]
        ]
        page += 1
        break  # TODO REMOVE

    mangadex_items.sort(key=lambda x: x.title)
    return mangadex_items


def fetch_mangadex_item(mangadex_id: str) -> Optional[MangadexItem]:
    """
    Fetches information for a mangadex
    """
    url = "https://api.mangadex.org/manga"
    response = requests.get(url, params={"ids[]": mangadex_id})

    if response.status_code >= 300:
        return None

    data = json.loads(response.text)["data"]
    return MangadexItem.from_json(data)
