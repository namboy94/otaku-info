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
from puffotter.flask.base import db
from otaku_info.db.MediaId import MediaId
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.LnRelease import LnRelease
from otaku_info.utils.dates import map_month_name_to_month_number
from otaku_info.utils.enums import MediaType, ListService
from otaku_info.utils.anilist.api import load_media_info, \
    map_myanimelist_id_to_anilist_id
from otaku_info.background.anilist import update_media_id, update_media_item


def load_tables(year: int) -> List[BeautifulSoup]:
    """
    Loads the tables containing the release data
    """
    current_year = datetime.utcnow().year

    # TODO Parse years from 2015-2017
    if year < 2018 or year > current_year + 1:
        return []

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

    return tables


def parse_release(year: int, parts: List[BeautifulSoup]) -> LnRelease:
    """
    Parses a light novel release table entry and turns it into
    an LnRelease object.
    The LnRelease entry in the database is also updated if it already exists
    :param year: The year of the release
    :param parts: The parts of the table entry
    :return: The resulting LnRelease object
    """

    release_date_string = parts[0].text
    month_name, day_string = release_date_string.split(" ")
    month = map_month_name_to_month_number(month_name)
    try:
        day = int(day_string)
    except ValueError:
        day = 1
    release_date = datetime(year=year, month=month, day=day)
    release_date_string = release_date.strftime("%Y-%m-%d")

    series_name = parts[1].text
    volume = parts[2].text
    publisher = parts[3].text

    purchase_link_item = parts[3].find("a")
    purchase_link = None
    if purchase_link_item is not None:
        purchase_link = purchase_link_item["href"]

    info_link_item = parts[1].find("a")
    info_link = None
    if info_link_item is not None:
        info_link = info_link_item["href"]

    digital = "digital" in parts[4].text.lower()
    physical = "physical" in parts[4].text.lower()

    media_item = get_media_item(info_link)

    release: LnRelease = LnRelease.query.filter_by(
        series_name=series_name,
        volume=volume,
        digital=digital,
        physical=physical,
        publisher=publisher
    ).first()
    is_new = False
    if release is None:
        release = LnRelease(
            series_name=series_name,
            volume=volume,
            digital=digital,
            physical=physical,
            publisher=publisher
        )
        is_new = True

    release.release_date_string = release_date_string
    release.purchase_link = purchase_link
    release.media_item = media_item

    if is_new:
        db.session.add(release)

    db.session.commit()
    return release


def get_media_item(info_link: str) -> Optional[MediaItem]:
    """
    Retrieves the media item for an info link
    Automatically adds missing entries to the database
    :param info_link: The info link
    :return: The media item or None if no media item can be found
    """

    if info_link is None or "myanimelist.net" not in info_link:
        return None

    url_parts = info_link.split("/")
    index = -1
    while not url_parts[index].isdigit():
        index -= 1
    myanimelist_id = url_parts[index]

    existing = MediaId.query.filter_by(
        service_id=myanimelist_id,
        service=ListService.MYANIMELIST
    ).all()
    existing = [
        x for x in existing
        if x.media_item.media_type == MediaType.MANGA
    ]

    if len(existing) != 0:
        return existing[0].media_item
    else:
        anilist_id = map_myanimelist_id_to_anilist_id(
            int(myanimelist_id), MediaType.MANGA
        )

        if anilist_id is None:
            return None

        existing = MediaId.query.filter_by(
            service_id=str(anilist_id),
            service=ListService.ANILIST
        ).all()
        existing = [
            x for x in existing
            if x.media_item.media_type == MediaType.MANGA
        ]

        if len(existing) == 0:
            media_info = load_media_info(anilist_id, MediaType.MANGA)
            if media_info is None:
                media_item = None
            else:
                media_item = update_media_item(media_info, None)
                update_media_id(media_info, media_item, None)
        else:
            anilist_id_obj = existing[0]
            media_item = anilist_id_obj.media_item

        if media_item is not None:
            myanimelist_id_obj = MediaId(
                media_item=media_item,
                service=ListService.MYANIMELIST,
                service_id=str(myanimelist_id)
            )
            db.session.add(myanimelist_id_obj)
            db.session.commit()
        return media_item


def load_ln_releases(year: int) -> List[LnRelease]:
    """
    Loads the currently available light novel releases from reddit's
    /r/lightnovels subreddit.
    :param year: Specifies the year of the releases
    :return: The releases as LnRelease objects
    """
    tables = load_tables(year)

    releases: List[LnRelease] = []
    for i, table in enumerate(tables):
        month_number = i + 1

        for entry in table.find_all("tr"):
            release = parse_release(year, entry.find_all("td"))

            if month_number != release.release_date.month:
                print(f"Incorrect month: "
                      f"{month_number} != {release.release_date.month} "
                      f"({release.release_date_string})")

            releases.append(release)

    return releases
