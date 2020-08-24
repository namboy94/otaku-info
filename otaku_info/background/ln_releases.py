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
from typing import Dict, Tuple, cast, Optional
from puffotter.flask.base import app, db
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaId import MediaId
from otaku_info.db.LnRelease import LnRelease
from otaku_info.enums import MediaType, ListService
from otaku_info.external.reddit import load_ln_releases
from otaku_info.external.myanimelist import load_myanimelist_item
from otaku_info.external.anilist import load_anilist_info
from otaku_info.external.entities.RedditLnRelease import RedditLnRelease
from otaku_info.utils.db.updater import update_or_insert_item
from otaku_info.utils.db.convert import anime_list_item_to_media_item, \
    anime_list_item_to_media_id, ln_release_from_reddit_item
from otaku_info.utils.db.load import load_existing_media_data


def update_ln_releases():
    """
    Updates the light novel releases
    :return: None
    """
    start = time.time()
    app.logger.info("Starting Light Novel Release Update")
    ln_releases = load_ln_releases()
    existing_releases: Dict[Tuple, LnRelease] = {
        x.identifier_tuple: x
        for x in LnRelease.query.all()
    }
    media_items, media_ids, _ = load_existing_media_data()
    series_media_items = {}
    for existing in existing_releases.values():
        key = existing.series_name
        if existing.media_item is not None:
            if key in series_media_items:
                other_id = series_media_items[key].media_item_id
                if existing.media_item_id != other_id:
                    app.logger.warning(f"Different Media Items for {key}")
            series_media_items[key] = existing

    for ln_release in ln_releases:
        release = ln_release_from_reddit_item(ln_release, None)
        identifier = release.identifier_tuple
        existing = existing_releases.get(identifier)

        if existing is None:
            media_item = create_media_item_from_reddit_ln_release(
                ln_release, media_items, media_ids
            )
            media_item_id = None if media_item is None else media_item.id
            release.media_item_id = media_item_id
        elif existing.media_item_id is None:
            if release.series_name in series_media_items:
                release.media_item_id = \
                    series_media_items[release.series_name].media_item_id
            else:
                media_item = create_media_item_from_reddit_ln_release(
                    ln_release, media_items, media_ids
                )
                media_item_id = None if media_item is None else media_item.id
                release.media_item_id = media_item_id
        else:
            release.media_item_id = existing.media_item_id

        update_or_insert_item(release, existing_releases)

    db.session.commit()
    app.logger.info(f"Finished Light Novel Release Update "
                    f"in {time.time() - start}s.")


def create_media_item_from_reddit_ln_release(
        ln_release: RedditLnRelease,
        media_items: Dict[Tuple, MediaItem],
        media_ids: Dict[Tuple, MediaId]
) -> Optional[MediaItem]:
    """
    Creates a media item based on a reddit ln release
    Fills any missing entries in the database
    :param ln_release: The ln release
    :param media_items: Existing media items
    :param media_ids: Existing media ids
    :return: The media item
    """

    mal_id = ln_release.myanimelist_id
    anilist_id = ln_release.anilist_id

    if mal_id is None:
        return None
    elif anilist_id is not None:
        info = load_anilist_info(anilist_id, MediaType.MANGA)
    else:
        info = load_myanimelist_item(mal_id, MediaType.MANGA)

    if info is None:
        return None
    else:
        media_item = anime_list_item_to_media_item(info)
        media_item = cast(MediaItem, update_or_insert_item(
            media_item, media_items
        ))
        media_id = anime_list_item_to_media_id(info, media_item)
        update_or_insert_item(media_id, media_ids)
        if info.service == ListService.ANILIST:
            media_id = anime_list_item_to_media_id(
                info, media_item, ListService.MYANIMELIST
            )
            update_or_insert_item(media_id, media_ids)

        return media_item
