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

from otaku_info.test.TestFramework import _TestFramework
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaId import MediaId
from otaku_info.utils.db.DbQueue import DbQueue
from otaku_info.enums import MediaType, MediaSubType, ReleasingState, \
    ConsumingState, ListService


class TestDbQueue(_TestFramework):

    def test_inserting_full_media_items(self):
        user = self.generate_sample_user(True)[0]
        media_item_params = {
            "media_type": MediaType.MANGA,
            "media_subtype": MediaSubType.MANGA,
            "english_title": "English",
            "romaji_title": "Japanese",
            "cover_url": "Cover",
            "latest_release": 10,
            "latest_volume_release": 1,
            "releasing_state": ReleasingState.RELEASING,
            "next_episode": None,
            "next_episode_airing_time": None
        }
        user_state_params = {
            "user_id": user.id,
            "progress": 5,
            "volume_progress": 0,
            "score": 77,
            "consuming_state": ConsumingState.CURRENT
        }
        media_list_params = {
            "user_id": user.id,
            "name": "List",
            "service": ListService.ANILIST,
            "media_type": MediaType.MANGA
        }

        DbQueue.queue_media_item(
            media_item_params,
            ListService.ANILIST,
            {ListService.ANILIST: "1", ListService.MYANIMELIST: "2"},
            user_state_params,
            media_list_params
        )

        self.assertEqual(len(MediaItem.query.all()), 0)
        self.assertEqual(len(MediaId.query.all()), 0)
        DbQueue.process_queue()
        self.assertEqual(len(MediaItem.query.all()), 1)
        self.assertEqual(len(MediaId.query.all()), 2)

        media_item: MediaItem = MediaItem.query.all()[0]
        self.assertEqual(media_item.english_title, "English")
        self.assertEqual(len(media_item.media_ids), 2)

        media_item_params["english_title"] = "LALA"

        DbQueue.queue_media_item(
            media_item_params,
            ListService.MANGADEX,
            {
                ListService.ANILIST: "1",
                ListService.MANGADEX: "3",
                ListService.KITSU: "4"
            },
        )
        DbQueue.process_queue()
        self.assertEqual(len(MediaItem.query.all()), 1)
        self.assertEqual(len(MediaId.query.all()), 4)

        media_item: MediaItem = MediaItem.query.all()[0]
        self.assertEqual(media_item.english_title, "LALA")
        self.assertEqual(len(media_item.media_ids), 4)
