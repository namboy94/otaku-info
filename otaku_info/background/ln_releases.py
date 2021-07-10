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
from typing import Dict
from jerrycan.base import app, db
from otaku_info.db import MediaIdMapping
from otaku_info.db.MediaItem import MediaItem
from otaku_info.enums import ListService, MediaType
from otaku_info.external.reddit import load_ln_releases
from otaku_info.utils.object_conversion import anime_list_item_to_media_item, \
    reddit_ln_release_to_ln_release
from otaku_info.external.myanimelist import load_myanimelist_item
from otaku_info.external.anilist import load_anilist_info


def update_ln_releases():
    """
    Updates the light novel releases
    :return: None
    """
    start = time.time()
    app.logger.info("Starting Reddit LN Update")

    existing_myanimelist_items: Dict[int, MediaItem] = {
        int(x.service_id): x
        for x in MediaItem.query.filter_by(
            service=ListService.MYANIMELIST
        ).options(db.joinedload(MediaItem.id_mappings)).all()
    }
    existing_anilist_items: Dict[int, MediaItem] = {
        int(x.service_id): x
        for x in MediaItem.query.filter_by(
            service=ListService.ANILIST
        ).options(db.joinedload(MediaItem.id_mappings)).all()
    }
    myanimelist_anilist_items = {}
    for anilist_id, anilist_item in existing_anilist_items.items():
        mal_mapping = anilist_item.ids.get(ListService.MYANIMELIST)
        if mal_mapping is not None:
            mal_id = int(mal_mapping.service_id)
            myanimelist_anilist_items[mal_id] = anilist_item

    ln_releases = load_ln_releases()
    for ln_release in ln_releases:

        items = []
        if ln_release.myanimelist_id is not None:
            mal_id = ln_release.myanimelist_id
            mal_item = existing_myanimelist_items.get(mal_id)
            anilist_item = myanimelist_anilist_items.get(mal_id)

            if mal_item is None:
                mal_info = load_myanimelist_item(mal_id, MediaType.MANGA)
                if mal_info is not None:
                    mal_item = anime_list_item_to_media_item(mal_info)
                    app.logger.debug(
                        f"Upserting myanimelist: {mal_item.english_title}"
                    )
                    mal_item = db.session.merge(mal_item)
                    existing_myanimelist_items[mal_id] = mal_item
            if anilist_item is None:
                anilist_info = load_anilist_info(
                    int(mal_id), MediaType.MANGA, ListService.MYANIMELIST
                )
                if anilist_info is not None:
                    anilist_item = anime_list_item_to_media_item(anilist_info)
                    app.logger.debug(
                        f"Upserting anilist: {anilist_item.english_title}"
                    )
                    anilist_item = db.session.merge(anilist_item)
                    myanimelist_anilist_items[mal_id] = anilist_item

            if anilist_item is not None and mal_item is not None:
                for one, two in [
                    (anilist_item, mal_item),
                    (mal_item, anilist_item)
                ]:
                    app.logger.debug(
                        f"Upserting mapping: "
                        f"{one.service.value}:{one.service_id}"
                        f"->{two.service.value}:{two.service_id}"
                    )
                    db.session.merge(MediaIdMapping(
                        service=one.service,
                        service_id=one.service_id,
                        media_type=one.media_type,
                        parent_service=two.service,
                        parent_service_id=two.service_id
                    ))
            items += [x for x in [anilist_item, mal_item] if x is not None]

        if len(items) == 0:
            items = [None]

        app.logger.debug(
            f"Upserting ln releases: {ln_release.series_name} "
            f"volume {ln_release.volume}"
        )
        for item in items:
            release = reddit_ln_release_to_ln_release(ln_release, item)

            db.session.merge(release)

        db.session.commit()

    app.logger.info(f"Finished Reddit LN Update in {time.time() - start}s.")
