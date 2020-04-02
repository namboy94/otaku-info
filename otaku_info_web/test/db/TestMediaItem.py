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

from sqlalchemy.exc import IntegrityError
from puffotter.flask.base import db
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.utils.enums import MediaType, MediaSubType, ReleasingState
from otaku_info_web.test.TestFramework import _TestFramework


class TestMediaItem(_TestFramework):
    """
    Class that tests the MediaItem database model
    """

    @staticmethod
    def generate_sample_media_item() -> MediaItem:
        """
        Generates a sample media item
        :return: The media item
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
        db.session.add(media_item)
        db.session.commit()
        return media_item

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        media_item = self.generate_sample_media_item()

        self.assertEqual(
            media_item.__json__(False),
            {
                "id": media_item.id,
                "media_type": media_item.media_type.value,
                "media_subtype": media_item.media_subtype.value,
                "english_title": media_item.english_title,
                "romaji_title": media_item.romaji_title,
                "cover_url": media_item.cover_url,
                "latest_release": media_item.latest_release,
                "releasing_state": media_item.releasing_state.value
            }
        )
        self.assertEqual(
            media_item.__json__(True),
            media_item.__json__(False)
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        media_item = self.generate_sample_media_item()
        data = media_item.__json__()
        data.pop("id")
        self.assertEqual(
            str(media_item),
            "MediaItem:{} <{}>".format(media_item.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        media_item = self.generate_sample_media_item()
        generated = {"value": media_item}
        code = repr(media_item)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], media_item)
        self.assertFalse(generated["value"] is media_item)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        media_item = self.generate_sample_media_item()
        media_item_2 = MediaItem(
            media_type=MediaType.MANGA,
            media_subtype=MediaSubType.MANGA,
            english_title="Don't Fly Me to the Moon",
            romaji_title="ATonikaku Cawaii",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/manga/"
                      "cover/medium/nx101177-FjjD5UWB3C3t.png",
            latest_release=None,
            releasing_state=ReleasingState.RELEASING
        )
        db.session.add(media_item_2)
        db.session.commit()
        mapping = {
            media_item: 100,
            media_item_2: 200
        }
        self.assertEqual(mapping[media_item], 100)
        self.assertEqual(mapping[media_item_2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        media_item = self.generate_sample_media_item()
        media_item_2 = MediaItem(
            media_type=MediaType.MANGA,
            media_subtype=MediaSubType.MANGA,
            english_title="Don't Fly Me to the Moon",
            romaji_title="ATonikaku Cawaii",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/manga/"
                      "cover/medium/nx101177-FjjD5UWB3C3t.png",
            latest_release=None,
            releasing_state=ReleasingState.RELEASING
        )
        db.session.add(media_item_2)
        db.session.commit()
        self.assertEqual(media_item, media_item)
        self.assertNotEqual(media_item, media_item_2)
        self.assertNotEqual(media_item, 100)

    def test_title(self):
        """
        Tests the title attribute of the media item
        :return: None
        """
        media_item = self.generate_sample_media_item()
        self.assertEqual(media_item.title, "Fly Me to the Moon")
        media_item.english_title = None
        self.assertEqual(media_item.title, "Tonikaku Cawaii")

    def test_uniqueness(self):
        """
        Tests that a mediaitem can only exist once
        :return: None
        """
        standard_kwargs = {
            "media_type": MediaType.MANGA,
            "media_subtype": MediaSubType.MANGA,
            "english_title": "ABC",
            "romaji_title": "DEF",
            "cover_url": "N/A",
            "latest_release": None,
            "releasing_state": ReleasingState.RELEASING
        }
        original = MediaItem(**standard_kwargs)
        db.session.add(original)
        db.session.commit()

        for key, value, error_expected in [
            ("media_type", MediaType.ANIME, False),
            ("media_subtype", MediaSubType.NOVEL, False),
            ("romaji_title", "XYZ", False),
            ("english_title", "ABCDE", True),
            ("cover_url", "AAA", True)
        ]:
            kwargs = dict(standard_kwargs)
            kwargs[key] = value
            try:
                generated = MediaItem(**kwargs)
                db.session.add(generated)
                db.session.commit()
                if error_expected:
                    self.fail()
            except IntegrityError as e:
                db.session.rollback()
                if not error_expected:
                    raise e
