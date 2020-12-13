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

import requests
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from jerrycan.base import app
from otaku_info.external.entities.RedditLnRelease import RedditLnRelease


def load_ln_releases(year: Optional[int] = None) -> List[RedditLnRelease]:
    """
    Loads the light novel releases
    """
    releases: List[RedditLnRelease] = []
    current_year = datetime.utcnow().year

    if year is None:
        for year in range(2018, current_year + 2):
            releases += load_ln_releases(year)
        return releases

    tables = load_tables(year)

    for i, table in enumerate(tables):
        month_number = i + 1

        for entry in table.find_all("tr"):
            release = RedditLnRelease.from_parts(year, entry.find_all("td"))

            if month_number != release.release_date.month:
                app.logger.debug(
                    f"Incorrect month: "
                    f"{month_number} != {release.release_date.month} "
                    f"({release.release_date}/{release.series_name})"
                )

            releases.append(release)

    return releases


def load_tables(year: int) -> List[BeautifulSoup]:
    """
    Loads the tables containing the release data
    """
    current_year = datetime.utcnow().year

    # TODO Parse years from 2015-2017
    if year < 2018 or year > current_year + 1:
        return []

    url = f"https://old.reddit.com/r/LightNovels/wiki/{year}releases"

    if year >= current_year:
        if requests.head(url).status_code >= 300:
            url = "https://old.reddit.com/r/LightNovels/wiki/upcomingreleases"

    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers).text
    soup = BeautifulSoup(resp, "html.parser")

    tables = soup.find_all("tbody")

    # Table 0: Releases for current month on side bar
    # Table 1: Table below current month releases on side bar
    # Table -1: To be announced
    tables = tables[2:-1]

    if url.endswith("upcomingreleases"):

        month_names = soup.find_all("h3")
        month_names.pop(0)
        month_names = [
            x.text.lower().split(" ")[0].strip() for x in month_names
        ]

        is_current_year = True
        filtered = []
        for i, month_name in enumerate(month_names):
            table = tables[i]

            if (year == current_year and is_current_year) or \
               (year > current_year and not is_current_year):
                filtered.append(table)

            if month_name == "december":
                is_current_year = False
        tables = filtered

        while year == current_year and len(tables) < 12:
            tables = [BeautifulSoup("")] + tables

    return tables
