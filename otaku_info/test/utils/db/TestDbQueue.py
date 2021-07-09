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
from otaku_info.db.MediaIdMapping import MediaId
from otaku_info.utils.db.DbQueue import DbQueue
from otaku_info.enums import MediaType, MediaSubType, ReleasingState, \
    ConsumingState, ListService


class TestDbQueue(_TestFramework):
    """
    Class that tests the database queue
    """

    def generate_params(self):
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

        params = [
            media_item_params,
            ListService.ANILIST,
            {ListService.ANILIST: "1", ListService.MYANIMELIST: "2"},
            user_state_params,
            media_list_params
        ]
        return params

    def test_inserting_full_media_items(self):
        """
        Tests inserting a correct and full media item, then updating it and
        adding some more service IDs
        :return: None
        """
        params = self.generate_params()

        DbQueue.queue_media_item(*params)

        self.assertEqual(len(MediaItem.query.all()), 0)
        self.assertEqual(len(MediaId.query.all()), 0)
        DbQueue.process_queue()
        self.assertEqual(len(MediaItem.query.all()), 1)
        self.assertEqual(len(MediaId.query.all()), 2)

        # Check repeated inserts
        DbQueue.queue_media_item(*params)
        DbQueue.queue_media_item(*params)
        DbQueue.queue_media_item(*params)
        DbQueue.process_queue()

        self.assertEqual(len(MediaItem.query.all()), 1)
        self.assertEqual(len(MediaId.query.all()), 2)
        media_item: MediaItem = MediaItem.query.all()[0]
        self.assertEqual(media_item.english_title, "English")
        self.assertEqual(len(media_item.media_ids), 2)

        # Check updating
        params[0]["english_title"] = "HAHA"
        DbQueue.queue_media_item(*params)
        DbQueue.process_queue()
        self.assertEqual(len(MediaItem.query.all()), 1)
        self.assertEqual(len(MediaId.query.all()), 2)
        media_item: MediaItem = MediaItem.query.all()[0]
        self.assertEqual(media_item.english_title, "HAHA")
        self.assertEqual(len(media_item.media_ids), 2)

        params[0]["english_title"] = "LALA"
        params = [
            params[0],
            ListService.MANGADEX,
            {
                ListService.ANILIST: "1",
                ListService.MANGADEX: "3",
                ListService.KITSU: "4"
            }
        ]

        DbQueue.queue_media_item(*params)
        DbQueue.process_queue()
        self.assertEqual(len(MediaItem.query.all()), 1)
        self.assertEqual(len(MediaId.query.all()), 4)

        media_item: MediaItem = MediaItem.query.all()[0]
        self.assertEqual(media_item.english_title, "LALA")
        self.assertEqual(len(media_item.media_ids), 4)

    def test_detecting_missing_service_id(self):
        """
        Tests if missing service IDs are handled correctly
        :return: None
        """
        DbQueue.queue_media_item({}, ListService.ANILIST, {})
        self.assertEqual(len(MediaItem.query.all()), 0)
        DbQueue.process_queue()
        self.assertEqual(len(MediaItem.query.all()), 0)

    def test_identical_media_items_with_different_ids(self):
        """
        Tests if adding two items that have the same information but different
        IDs are handled correctly.
        This can happen with some manga on anilist, for example.
        :return: None
        """
        params = self.generate_params()
        DbQueue.queue_media_item(*params)
        DbQueue.process_queue()

        self.assertEqual(len(MediaItem.query.all()), 1)
        self.assertEqual(len(MediaId.query.all()), 2)

        params[2] = {ListService.ANILIST: "10"}
        DbQueue.queue_media_item(*params)
        DbQueue.process_queue()

        # TODO handles this more nicely
        # For example: Creating two media items
        self.assertEqual(len(MediaItem.query.all()), 1)
        self.assertEqual(len(MediaId.query.all()), 2)
        anilist_id = \
            MediaId.query.filter_by(service=ListService.ANILIST).first()
        self.assertEqual(anilist_id.service_id, "1")

    def test_changing_media_subtype(self):
        params = self.generate_params()
        params[0]["media_type"] = MediaType.ANIME
        params[0]["media_subtype"] = MediaSubType.SPECIAL
        DbQueue.queue_media_item(*params)
        DbQueue.process_queue()

        media_item: MediaItem = MediaItem.query.all()[0]
        self.assertEqual(media_item.media_subtype, MediaSubType.SPECIAL)
        for media_id in MediaId.query.all():  # type: MediaId
            self.assertEqual(media_id.media_subtype, MediaSubType.SPECIAL)

        params[0]["media_subtype"] = MediaSubType.OVA
        DbQueue.queue_media_item(*params)
        DbQueue.process_queue()

        # TODO

        # media_item = MediaItem.query.all()[0]
        # self.assertEqual(media_item.media_subtype, MediaSubType.OVA)
        # for media_id in MediaId.query.all():  # type: MediaId
        #     self.assertEqual(media_id.media_subtype, MediaSubType.OVA)

        # Note: This has different bahviour on postgres than it does on sqlite
        # Sqlite automatically updates the media ids, but postgres will
        # break.
        # This is fixed by adding cascades to the foreign key constraint
        # in the database definitions
        # This test won't find an issue here when using sqlite though.
