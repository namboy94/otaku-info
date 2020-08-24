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
from typing import Dict, Optional, Tuple, cast
from puffotter.flask.base import app, db
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaId import MediaId
from otaku_info.enums import ListService, MediaType
from otaku_info.external.anilist import load_anilist_info
from otaku_info.external.myanimelist import load_myanimelist_item
from otaku_info.external.mangadex import fetch_mangadex_item
from otaku_info.external.entities.MangadexItem import MangadexItem
from otaku_info.utils.db.updater import update_or_insert_item
from otaku_info.utils.db.convert import mangadex_item_to_media_item, \
    anime_list_item_to_media_item
from otaku_info.utils.db.load import load_existing_media_data, load_service_ids
from otaku_info.mappings import list_service_priorities


def update_mangadex_data(
        start: int = 1,
        end: Optional[int] = None,
        refresh: bool = False
):
    """
    Goes through mangadex IDs sequentially and stores ID mappings for
    these entries if found.
    Stops once 100 consecutive entries didn't return any results
    :param start: Optionally specifies a starting index
    :param end: Optionally specifies an ending index
    :param refresh: If true, will update existing mangadex info
    :return: None
    """
    start_time = time.time()
    app.logger.info("Starting Mangadex Update")
    endcounter = 0
    mangadex_id = start - 1

    existing_ids, existing_media_items, existing_media_ids = __update_cache()
    while True:
        mangadex_id += 1

        if mangadex_id % 100 == 0:
            db.session.commit()
            existing_ids, existing_media_items, existing_media_ids = \
                __update_cache()

        if mangadex_id == end or endcounter > 100:
            break
        elif str(mangadex_id) in existing_ids[ListService.MANGADEX] \
                and not refresh:
            continue

        app.logger.debug(f"Probing mangadex id {mangadex_id}")
        mangadex_item = fetch_mangadex_item(mangadex_id)
        if mangadex_item is None:
            endcounter += 1
            app.logger.debug("Couldn't load mangadex info")
            continue
        else:
            endcounter = 0

        __update_database_with_mangadex_item(
            mangadex_item,
            existing_ids,
            existing_media_items,
            existing_media_ids
        )

    db.session.commit()
    app.logger.info(f"Finished Mangadex Update in "
                    f"{time.time() - start_time}s.")


def __update_cache() -> Tuple[
    Dict[ListService, Dict[str, MediaId]],
    Dict[Tuple, MediaItem],
    Dict[Tuple, MediaId]
]:
    """
    :return: Existing database content used for mangadex operations
    """
    app.logger.debug("Refreshing mangadex cache")
    existing_ids = load_service_ids(MediaType.MANGA)
    existing_media_items, existing_media_ids, _ = \
        load_existing_media_data()
    return existing_ids, existing_media_items, existing_media_ids


def __update_database_with_mangadex_item(
        mangadex_item: MangadexItem,
        existing_ids: Dict[ListService, Dict[str, MediaId]],
        existing_media_items: Dict[Tuple, MediaItem],
        existing_media_ids: Dict[Tuple, MediaId]
):
    """
    Updates the database with the contents of a single mangadex item
    :param mangadex_item: The mangadex item
    :param existing_ids: Existing IDs mapped to list services
    :param existing_media_items: The existing media items
    :param existing_media_ids: The existing media IDs
    :return: None
    """
    media_item = __update_or_insert_mangadex_media_item(
        mangadex_item,
        existing_ids,
        existing_media_items
    )
    media_id_mapping = media_item.media_id_mapping

    for service, service_id in mangadex_item.external_ids.items():
        if service not in media_id_mapping:
            media_id = MediaId(
                media_item_id=media_item.id,
                media_type=media_item.media_type,
                service=service,
                service_id=service_id
            )
            update_or_insert_item(media_id, existing_media_ids)


def __update_or_insert_mangadex_media_item(
        mangadex_item: MangadexItem,
        existing_ids: Dict[ListService, Dict[str, MediaId]],
        existing_media_items: Dict[Tuple, MediaItem]
) -> Optional[MediaItem]:
    """
    Resolves the media item for a mangadex item
    Will create the media item and prune superfluous media items
    :param mangadex_item: The mangadex item
    :param existing_ids: Existing IDs mapped to list services
    :param existing_media_items: The existing media items
    :return: The media item
    """
    existing_mapped_ids = {}
    for service, service_id in mangadex_item.external_ids.items():
        media_id = existing_ids[service].get(service_id)
        if media_id is not None:
            existing_mapped_ids[media_id.service] = media_id

    media_item = None
    if len(existing_mapped_ids) == 0:

        for service in [ListService.ANILIST, ListService.MYANIMELIST]:
            if media_item is None and service in mangadex_item.external_ids:
                media_item = __load_anime_list_based_media_item(
                    mangadex_item, service, existing_media_items
                )
        if media_item is None:
            media_item = mangadex_item_to_media_item(mangadex_item)
            media_item = cast(MediaItem, update_or_insert_item(
                media_item, existing_media_items
            ))
    else:
        # Ensure that all have the same media item
        for service in list_service_priorities:
            if service in existing_mapped_ids:
                media_item = existing_mapped_ids[service].media_item

        for service, media_id in existing_mapped_ids.items():
            if media_id.media_item != media_item:
                # Delete duplicate media items
                db.session.delete(media_id.media_item)
                db.session.commit()

    return media_item


def __load_anime_list_based_media_item(
        mangadex_item: MangadexItem,
        service: ListService,
        existing_media_items: Dict[Tuple, MediaItem]
) -> Optional[MediaItem]:
    """
    Inserts or Updates a media item based on anilist data for a mangadex item
    :param mangadex_item: The mangadex item
    :param existing_media_items: Existing media items
    :return: The media item
    """
    service_id = mangadex_item.external_ids[service]

    if service == ListService.ANILIST:
        service_item = load_anilist_info(int(service_id), MediaType.MANGA)
    elif service == ListService.MYANIMELIST:
        service_item = load_myanimelist_item(int(service_id), MediaType.MANGA)
    else:
        service_item = None

    if service_item is None:
        return None

    media_item = anime_list_item_to_media_item(service_item)
    media_item = cast(MediaItem, update_or_insert_item(
        media_item, existing_media_items
    ))
    return media_item
