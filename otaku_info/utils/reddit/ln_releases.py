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
from otaku_info.utils.reddit.LnRelease import LnRelease


def load_ln_releases(year: Optional[int] = None, month: Optional[int] = None) \
        -> List[LnRelease]:
    """
    Loads the currently available light novel releases from reddit's
    /r/lightnovels subreddit.
    :param year: Specifies the year. Defaults to the current year.
    :param month: Can be used to filter out any releases not in the
                  specified month
    :return: The releases as LnRelease objects
    """
    releases: List[LnRelease] = []

    today = datetime.utcnow()
    current_year = today.year

    if year is None:
        year = current_year

    # TODO Parse years from 2015-2017
    if year < 2018 or year > current_year + 1:
        return releases

    if year >= current_year:
        url = "https://old.reddit.com/r/LightNovels/wiki/upcomingreleases"
    else:
        url = f"https://old.reddit.com/r/LightNovels/wiki/{year}releases"

    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers).text
    soup = BeautifulSoup(resp, "html.parser")

    tables = soup.find_all("tbody")

    # Table 0: Releases for current month on side bar
    # Table 1: Table below current month releases on side bar
    # Table -1: To be announced
    tables = tables[2:-1]

    if year >= current_year:
        if year == current_year:
            tables = tables[0:12]
        else:
            tables = tables[12:]

    for i, table in enumerate(tables):
        month_number = i + 1

        for entry in table.find_all("tr"):
            parts = entry.find_all("td")

            info_link_item = parts[1].find("a")
            purchase_link_item = parts[3].find("a")
            info_link = None
            purchase_link = None
            if info_link_item is not None:
                info_link = info_link_item["href"]
            if purchase_link_item is not None:
                purchase_link = purchase_link_item["href"]

            ln_release = LnRelease(
                year=year,
                release_date_string=parts[0].text,
                series_name=parts[1].text,
                info_link=info_link,
                volume=parts[2].text,
                publisher=parts[3].text,
                purchase_link=purchase_link,
                digital="digital" in parts[4].text,
                physical="physical" in parts[4].text
            )

            if month_number != ln_release.release_date.month:
                print(f"Incorrect month: "
                      f"{month_number} != {ln_release.release_date.month} "
                      f"({ln_release.release_date_string})")

            releases.append(ln_release)

    if month is not None:
        releases = list(filter(
            lambda x: x.release_date.month == month,
            releases
        ))
    return releases
