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
from typing import Dict


def load_newest_episodes() -> Dict[int, int]:
    """
    Loads the newest episode numbers on /r/anime's /u/autolovepon's page
    :return: The show's anilist ID mapped to the latest episode number
    """
    url = "https://old.reddit.com/user/AutoLovepon.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)

    latest = {}
    entries = data["data"]["children"]

    for entry in entries:
        try:
            title = entry["data"]["title"].lower()
            name = title.split(" - episode ")[0].lower()
            episode = title.split(" - episode ")[1].split(" discussion")[0]

            text = entry["data"]["selftext"].lower()

            anilist_id = \
                text.split("https://anilist.co/anime/")[1].split(")")[0]
            anilist_id = int(anilist_id)

            latest[anilist_id] = max(latest.get(name, 0), int(episode))

        except IndexError:
            pass

    return latest
