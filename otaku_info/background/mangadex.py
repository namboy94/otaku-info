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
from typing import Optional
from jerrycan.base import app, db
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaIdMapping import MediaIdMapping
from otaku_info.enums import ListService, MediaType
from otaku_info.external.entities.AnimeListItem import AnimeListItem
from otaku_info.external.mangadex import fetch_all_mangadex_items
from otaku_info.external.anilist import load_anilist_info
from otaku_info.external.myanimelist import load_myanimelist_item
from otaku_info.utils.object_conversion import anime_list_item_to_media_item, \
    mangadex_item_to_media_item


def update_mangadex_data():
    """
    Loads the newest mangadex information and updates the mangadex entries in
    the database.
    :return: None
    """
    start_time = time.time()
    app.logger.info("Starting Mangadex Update")

    _existing_items = MediaItem.query.all()
    existing_items = {
        service: {
            x.service_id: x
            for x in _existing_items
            if x.service == service
        }
        for service in ListService
    }

    for mangadex_item in fetch_all_mangadex_items():

        media_item = mangadex_item_to_media_item(mangadex_item)
        app.logger.debug(f"Upserting mangadex item {media_item.title}")
        media_item = db.session.merge(media_item)

        ids = mangadex_item.external_ids
        ids[ListService.MANGADEX] = mangadex_item.mangadex_id

        items = [media_item]

        for service in [ListService.ANILIST]:  # ListService.MYANIMELIST

            service_id = ids.get(service)
            existing = existing_items[service].get(service_id)

            if service_id is None:
                continue
            if existing is not None:
                items.append(existing)
                continue

            data: Optional[AnimeListItem] = None
            if service == ListService.ANILIST:
                data = load_anilist_info(
                    int(service_id), MediaType.MANGA
                )
            elif service == ListService.MYANIMELIST:
                data = load_myanimelist_item(
                    int(service_id), MediaType.MANGA
                )
            if data is not None:
                anime_item = anime_list_item_to_media_item(data)
                title = anime_item.title
                app.logger.debug(f"Upserting {service.value} item {title}")
                anime_item = db.session.merge(anime_item)
                existing_items[service][service_id] = anime_item
                items.append(anime_item)

        for item in items:
            if item is None:
                continue

            for service, _id in ids.items():
                if service == item.service:
                    continue

                mapping = MediaIdMapping(
                    parent_service=item.service,
                    parent_service_id=item.service_id,
                    media_type=item.media_type,
                    service=service,
                    service_id=_id
                )
                app.logger.debug(f"Upserting ID mapping "
                                 f"{item.service.value}:{item.service_id} -> "
                                 f"{service.value}:{_id}")
                db.session.merge(mapping)

        db.session.commit()

    app.logger.info(f"Finished Mangadex Update in "
                    f"{time.time() - start_time}s.")
