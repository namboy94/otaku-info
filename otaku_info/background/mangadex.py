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
from typing import Optional, Dict
from jerrycan.base import app, db
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaIdMapping import MediaId
from otaku_info.enums import ListService, MediaType, MediaSubType
from otaku_info.external.entities.AnimeListItem import AnimeListItem
from otaku_info.external.mangadex import fetch_all_mangadex_items
from otaku_info.external.anilist import load_anilist_info
from otaku_info.external.myanimelist import load_myanimelist_item
from otaku_info.utils.db.DbQueue import DbQueue


def update_mangadex_data():
    """
    Loads the newest mangadex information and updates the mangadex entries in
    the database.
    :return: None
    """
    start_time = time.time()
    app.logger.info("Starting Mangadex Update")

    existing_media_items: Dict[str, MediaItem] = {
        x.service_id: x.media_item
        for x in MediaId.query
        .filter_by(service=ListService.MANGADEX)
        .options(db.joinedload(MediaId.media_item))
        .all()
    }

    for mangadex_item in fetch_all_mangadex_items():

        media_item_params = {
            "media_type": MediaType.MANGA,
            "media_subtype": MediaSubType.MANGA,
            "english_title": mangadex_item.title,
            "romaji_title": mangadex_item.title,
            "cover_url": mangadex_item.cover_url,
            "latest_release": mangadex_item.total_chapters,
            "releasing_state": mangadex_item.releasing_state
        }
        service = ListService.MANGADEX
        service_ids = mangadex_item.external_ids
        service_ids[ListService.MANGADEX] = mangadex_item.mangadex_id

        # Skip existing items
        existing_item = existing_media_items.get(mangadex_item.mangadex_id)
        if existing_item is not None:
            all_ids_in_db = True
            for service in service_ids.keys():
                if service not in existing_item.media_id_mapping.keys():
                    all_ids_in_db = False
            if all_ids_in_db:
                continue

        better_item: Optional[AnimeListItem] = None
        if ListService.ANILIST in service_ids:
            better_item = load_anilist_info(
                int(service_ids[ListService.ANILIST]),
                MediaType.MANGA
            )
            service = ListService.ANILIST
        elif ListService.MYANIMELIST in service_ids:
            better_item = load_myanimelist_item(
                int(service_ids[ListService.MYANIMELIST]),
                MediaType.MANGA
            )
            service = ListService.MYANIMELIST

        if better_item is not None:
            media_item_params = {
                "media_type": MediaType.MANGA,
                "media_subtype": better_item.media_subtype,
                "english_title": better_item.english_title,
                "romaji_title": better_item.romaji_title,
                "cover_url": better_item.cover_url,
                "latest_release": better_item.latest_release,
                "releasing_state": better_item.releasing_state
            }

        DbQueue.queue_media_item(media_item_params, service, service_ids)

    app.logger.info(f"Finished Mangadex Update in "
                    f"{time.time() - start_time}s.")
