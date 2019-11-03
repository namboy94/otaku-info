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

import requests
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


def load_ln_releases(year: Optional[int] = None, month: Optional[str] = None) \
        -> Dict[int, Dict[str, List[Dict[str, str]]]]:
    """
    Loads the currently available light novel releases from reddit's
    /r/lightnovels subreddit.
    :param year: Limits releases to a specific year
    :param month: Limits releases to a specific month
    :return: The releases, categorized by year and month
    """
    releases = {}  # type: Dict[int, Dict[str, List[Dict[str, str]]]]

    page = "https://old.reddit.com/r/LightNovels/wiki/upcomingreleases"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(page, headers=headers).text
    soup = BeautifulSoup(resp, "html.parser")

    years = soup.find_all("h2")
    years = years[5:]
    years = years[:-1]
    years = list(map(lambda x: int(x.text), years))

    months = [
        "january", "february", "march", "april",
        "may", "june", "july", "august",
        "september", "october", "november", "december"
    ]

    for _year in years:
        releases[_year] = {}
        for _month in months:
            releases[_year][_month] = []

    tables = soup.find_all("tbody")
    tables = tables[2:-1]

    current_year = years.pop(0)
    first_table = True
    for table in tables:
        first_entry = True
        for entry in table.find_all("tr"):

            parts = entry.find_all("td")
            title = parts[1].text

            try:
                int(title)
                continue
            except ValueError:
                pass

            _month, day = parts[0].text.split(" ", 1)
            _month = _month.lower()
            volume = parts[2].text

            if first_entry and month == "January" and not first_table:
                current_year = years.pop(0)
            first_entry = False

            releases[current_year][_month].append({
                "title": title,
                "volume": volume,
                "day": day,
                "release_type": parts[4].text
            })

        first_table = False

    if year is not None:
        releases = {year: releases.get(year, {})}
    if month is not None:
        _releases = {}  # type: Dict[int, Dict[str, List[Dict[str, str]]]]
        for year, data in releases.items():
            _releases[year] = {month: data.get(month, [])}
        releases = _releases

    return releases
