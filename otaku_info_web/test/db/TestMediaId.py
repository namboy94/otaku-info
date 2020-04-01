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

from typing import Tuple
from puffotter.flask.base import db
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.utils.enums import ListService, MediaType, MediaSubType, \
    ReleasingState
from otaku_info_web.test.TestFramework import _TestFramework


class TestMediaId(_TestFramework):
    """
    Class that tests the MediaId database model
    """

    @staticmethod
    def generate_sample_media_id() -> Tuple[MediaItem, MediaId]:
        """
        Generates a media id
        :return: The media item and media id
        """
        media_item = MediaItem(
            media_type=MediaType.MANGA,
            media_subtype=MediaSubType.MANGA,
            english_title="Fly Me to the Moon",
            romaji_title="Tonikaku Cawaii",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/manga/"
                      "cover/medium/nx101177-FjjD5UWB3C3t.png",
            latest_release=None,
            releasing_state=ReleasingState.RELEASING
        )
        media_id = MediaId(
            media_item=media_item,
            service_id=101177,
            service=ListService.ANILIST
        )
        db.session.add(media_item)
        db.session.add(media_id)
        db.session.commit()
        return media_item, media_id

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        media_item, media_id = self.generate_sample_media_id()

        self.assertEqual(
            media_id.__json__(False),
            {
                "id": media_id.id,
                "media_item_id": media_item.id,
                "service": media_id.service.value,
                "service_id": media_id.service_id
            }
        )
        self.assertEqual(
            media_id.__json__(True),
            {
                "id": media_id.id,
                "media_item": media_item.__json__(True),
                "media_item_id": media_item.id,
                "service": media_id.service.value,
                "service_id": media_id.service_id
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        media_item, media_id = self.generate_sample_media_id()
        data = media_id.__json__()
        data.pop("id")
        self.assertEqual(
            str(media_id),
            "MediaId:{} <{}>".format(media_id.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        media_item, media_id = self.generate_sample_media_id()
        generated = {"value": media_id}
        code = repr(media_id)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], media_id)
        self.assertFalse(generated["value"] is media_id)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        media_item, media_id = self.generate_sample_media_id()
        media_id_2 = MediaId(
            media_item=media_item,
            service_id=101178,
            service=ListService.ANILIST
        )
        db.session.add(media_id_2)
        db.session.commit()
        mapping = {
            media_id: 100,
            media_id_2: 200
        }
        self.assertEqual(mapping[media_id], 100)
        self.assertEqual(mapping[media_id_2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        media_item, media_id = self.generate_sample_media_id()
        media_id_2 = MediaId(
            media_item=media_item,
            service_id=101178,
            service=ListService.ANILIST
        )
        db.session.add(media_id_2)
        db.session.commit()
        self.assertEqual(media_id, media_id)
        self.assertNotEqual(media_id, media_id_2)
        self.assertNotEqual(media_id, 100)

    def test_generating_service_url(self):
        """
        Tests generating the generating of service URLs
        :return: None
        """
        _, media_id = self.generate_sample_media_id()
        urls = {
            ListService.ANILIST: "https://anilist.co/manga/101177",
            ListService.MYANIMELIST: "https://myanimelist.net/manga/101177",
            ListService.MANGADEX: "https://mangadex.org/title/101177"
        }
        for service in ListService:
            expected = urls[service]
            media_id.service = service
            self.assertEqual(media_id.service_url, expected)
