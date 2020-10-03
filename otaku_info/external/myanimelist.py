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

import time
import json
import requests
from typing import Optional
from jerrycan.base import app
from otaku_info.enums import MediaType
from otaku_info.external.entities.MyanimelistItem import MyanimelistItem


def load_myanimelist_item(myanimelist_id: int, media_type: MediaType) \
        -> Optional[MyanimelistItem]:
    """
    Loads myanimelist data using the jikan API
    :param myanimelist_id: The myanimelist ID
    :param media_type: The media type
    :return: The myanimelist item
    """
    url = f"https://api.jikan.moe/v3/{media_type.value}/{myanimelist_id}"
    response = requests.get(url)

    if response.status_code == 503:
        # Sometimes jikan temporarily loses connection to myanimelist
        time.sleep(2)
        response = requests.get(url)
    if response.status_code < 300:
        return None

    data = json.loads(response.text)
    if data["type"] == "BadResponseException":
        return None
    elif data["type"] == "RateLimitException":
        time.sleep(30)
        app.logger.warning("Rate limited by jikan")
        return load_myanimelist_item(myanimelist_id, media_type)

    mal_item = MyanimelistItem.from_query(media_type, data)
    return mal_item
