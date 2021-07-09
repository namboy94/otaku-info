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

from otaku_info.db.MediaIdMapping import MediaIdMapping
from otaku_info.enums import MediaType, ListService
from otaku_info.external.reddit import load_ln_releases
from otaku_info.external.myanimelist import load_myanimelist_item
from otaku_info.external.anilist import load_anilist_info
from otaku_info.utils.db.DbQueue import DbQueue


def update_ln_releases():
    """
    Updates the light novel releases
    :return: None
    """
    ln_releases = load_ln_releases()

    mal_ids = [
        x.service_id for x in
        MediaIdMappingquery.filter_by(
            media_type=MediaType.MANGA,
            service=ListService.MYANIMELIST
        ).all()
    ]

    for ln_release in ln_releases:

        service_ids = {ListService.MYANIMELIST: str(ln_release.myanimelist_id)}
        mal_id = str(ln_release.myanimelist_id)

        if ln_release.myanimelist_id is None:
            service_ids.pop(ListService.MYANIMELIST)

        if ln_release.myanimelist_id is not None and mal_id not in mal_ids:
            mal_ids.append(mal_id)
            anilist_id = ln_release.anilist_id

            if anilist_id is None:
                list_item = load_myanimelist_item(int(mal_id), MediaType.MANGA)
            else:
                list_item = load_anilist_info(anilist_id, MediaType.MANGA)
                service_ids[ListService.ANILIST] = str(anilist_id)

            if list_item is not None:
                media_item_params = {
                    "media_type": list_item.media_type,
                    "media_subtype": list_item.media_subtype,
                    "english_title": list_item.english_title,
                    "romaji_title": list_item.romaji_title,
                    "cover_url": list_item.cover_url,
                    "latest_release": list_item.latest_release,
                    "latest_volume_release": list_item.volumes,
                    "releasing_state": list_item.releasing_state,
                    "next_episode": list_item.next_episode,
                    "next_episode_airing_time":
                        list_item.next_episode_airing_time
                }
                DbQueue.queue_media_item(
                    media_item_params, ListService.MYANIMELIST, service_ids
                )
            else:
                service_ids = {}

        ln_params = {
            "release_date_string": ln_release.release_date_string,
            "series_name": ln_release.series_name,
            "volume": ln_release.volume,
            "publisher": ln_release.publisher,
            "purchase_link": ln_release.purchase_link,
            "digital": ln_release.digital,
            "physical": ln_release.physical
        }
        DbQueue.queue_ln_release(ln_params, service_ids)
