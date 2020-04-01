"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-web.

otaku-info-web is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-web is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-web.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import time
from puffotter.flask.base import db, app
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.utils.enums import ListService
from otaku_info_web.utils.mangadex.api import get_ids


def load_id_mappings():
    """
    Goes through mangadex IDs sequentially and stores ID mappings for
    these entries if found
    :return: None
    """
    mangadex_id = 0
    anilist_ids = {
        x.service_id: x for x in
        MediaId.query.filter_by(service=ListService.ANILIST).all()
    }

    endcounter = 0

    while True:
        time.sleep(0.5)
        mangadex_id += 1

        other_ids = get_ids(mangadex_id)

        if other_ids is None:
            endcounter += 1
            if endcounter > 1000:
                break
            else:
                continue
        else:
            endcounter = 0

        if ListService.ANILIST not in other_ids:
            continue

        anilist_id = int(other_ids[ListService.ANILIST])

        if anilist_id not in anilist_ids:
            continue

        media = anilist_ids[anilist_id].media_item
        existing = [
            x.service for x in
            MediaId.query.filter_by(media_item_id=media.id).all()
        ]

        app.logger.info("Found IDS using mangadex for mangadex id {}: {}"
                        .format(mangadex_id, other_ids))

        for list_service, _id in other_ids.items():

            if list_service in existing:
                continue

            media_id = MediaId(
                media_item=media,
                service=list_service,
                service_id=_id
            )
            db.session.add(media_id)
        db.session.commit()
