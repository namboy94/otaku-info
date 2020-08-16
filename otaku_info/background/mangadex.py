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
from typing import Dict, List, Optional, Tuple
from sqlalchemy.exc import IntegrityError
from puffotter.flask.base import db, app
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaId import MediaId
from otaku_info.utils.enums import ListService, MediaType
from otaku_info.utils.mangadex.api import get_external_ids
from otaku_info.utils.anilist.api import load_media_info


def load_id_mappings():
    """
    Goes through mangadex IDs sequentially and stores ID mappings for
    these entries if found
    :return: None
    """
    endcounter = 0
    mangadex_id = 0

    anilist_ids, existing_ids = load_db_content()

    while True:
        mangadex_id += 1

        if mangadex_id % 100 == 0:
            app.logger.debug("Refreshing mangadex cache")
            anilist_ids, existing_ids = load_db_content()

        app.logger.debug(f"Probing mangadex id {mangadex_id}")

        other_ids = get_external_ids(mangadex_id)

        if other_ids is None:
            endcounter += 1
            if endcounter > 1000:
                break
            else:
                continue
        else:
            endcounter = 0

        store_ids(existing_ids, anilist_ids, mangadex_id, other_ids)
    app.logger.info("Reached end of mangadex ID range")


def load_db_content() -> Tuple[
    Dict[str, MediaId],
    Dict[int, List[ListService]]
]:
    """
    Loads the existing data from the database.
    By doing this as few times as possible, we can greatly improve performance
    :return: The anilist IDs, The mangadex IDs mapped to other existing IDs
    """
    start = time.time()
    app.logger.debug("Starting caching of db data for mangadex ID mapping")

    all_ids: List[MediaId] = [
        x for x in
        MediaId.query.join(MediaItem).all()
        if x.media_item.media_type == MediaType.MANGA
    ]
    anilist_ids: Dict[str, MediaId] = {
        x.service_id: x
        for x in all_ids
        if x.service == ListService.ANILIST
    }

    mangadex_idmap: Dict[int, int] = {}

    existing_ids: Dict[int, List[ListService]] = {}
    for media_id in all_ids:
        media_item_id = media_id.media_item_id
        if media_item_id not in existing_ids:
            existing_ids[media_item_id] = []
        existing_ids[media_item_id].append(media_id)
        if media_id.service == ListService.MANGADEX:
            mangadex_idmap[media_item_id] = int(media_id.service_id)

    mapped_existing_ids = {
        mangadex_idmap[key]: value
        for key, value in existing_ids.items()
        if key in mangadex_idmap
    }

    app.logger.info(f"Finished caching of db data for mangadex ID mapping "
                    f"in {time.time() - start}s")
    return anilist_ids, mapped_existing_ids


def store_ids(
        existing_ids: Dict[int, List[ListService]],
        anilist_ids: Dict[str, MediaId],
        mangadex_id: int,
        other_ids: Dict[ListService, str]
):
    """
    Stores the fetched IDs in the database
    :param existing_ids: A dictionary mapping mangadex IDs to existing
                         list service types
    :param anilist_ids: Dictionary mapping anilist IDs to media IDs
    :param mangadex_id: The mangadex ID
    :param other_ids: The other IDs
    :return: None
    """
    if ListService.ANILIST not in other_ids:
        return

    existing_services = existing_ids.get(mangadex_id, [])
    existing_ids[mangadex_id] = existing_services
    anilist_id = other_ids[ListService.ANILIST]

    if anilist_id not in anilist_ids:
        media_item = create_anilist_media_item(int(anilist_id))
        if media_item is None:
            return
        else:
            media_item_id = media_item.id
    else:
        media_item_id = anilist_ids[anilist_id].media_item_id
        existing_services.append(ListService.ANILIST)

    app.logger.debug(f"Storing external IDS for mangadex id {mangadex_id}")

    for list_service, _id in other_ids.items():
        if list_service not in existing_services:
            media_id = MediaId(
                media_item_id=media_item_id,
                service=list_service,
                service_id=_id
            )
            db.session.add(media_id)
            existing_ids[mangadex_id].append(list_service)
            if list_service == ListService.ANILIST:
                anilist_ids[_id] = media_id

    try:
        db.session.commit()
    except IntegrityError:
        # Since mangadex has some entries that point to the exact same anilist
        # media item, we may sometimes encounter cases where we have two
        # mangadex IDs for one anilist ID.
        # By ignoring errors here, only the first mangadex ID will be stored.
        # An example for this issue is Genshiken (961) and its
        # sequel Genshiken Nidaime (962)
        db.session.rollback()
        app.logger.warning(f"Couldn't add mangadex ID {mangadex_id}")


def create_anilist_media_item(anilist_id: int) -> Optional[MediaItem]:
    """
    Creates an anilist media item using an anilist ID, fetching the data using
    the anilist API
    :param anilist_id: The anilist ID of the media
    :return: The generated Media Item
    """
    anilist_entry = load_media_info(anilist_id, MediaType.MANGA)
    if anilist_entry is None:
        return None
    media_item = MediaItem(
        media_type=MediaType.MANGA,
        media_subtype=anilist_entry.media_subtype,
        english_title=anilist_entry.english_title,
        romaji_title=anilist_entry.romaji_title,
        cover_url=anilist_entry.cover_url,
        latest_release=anilist_entry.latest_release,
        releasing_state=anilist_entry.releasing_state
    )
    db.session.add(media_item)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        app.logger.warning(f"Failed to add anilist manga entry "
                           f"(ID={anilist_id})")
        return None

    return media_item
