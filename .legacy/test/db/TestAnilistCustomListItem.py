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

from otaku_info_web.test.TestFramework import _TestFramework
from otaku_info_web.db.MediaItem import AnilistEntry
from otaku_info_web.db.AnilistUserEntry import AnilistUserEntry
from otaku_info_web.db.AnilistCustomList import AnilistCustomList
from otaku_info_web.db.AnilistCustomListItem import AnilistCustomListItem


class TestAnilistCustomListItem(_TestFramework):
    """
    Class that tests anilist custom list item database items
    """

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_list = AnilistCustomList(user=user, name="List")
        entry = AnilistEntry()
        custom_item = \
            AnilistCustomListItem(user=user, anilist="abc", vndb="xyz")
        self.db.session.add(custom_item)
        self.db.session.commit()
        self.assertEqual(
            custom_item.__json__(False),
            {
                "id": custom_item.id,
                "user_id": user.id,
                "anilist": "abc",
                "myanimelist": None,
                "kitsu": None,
                "bakaupdates": None,
                "mangadex": None,
                "vndb": "xyz",
                "anidb": None,
                "animeplanet": None,
                "lndb": None,
                "novelupdates": None,
            }
        ),
        self.assertEqual(
            custom_item.__json__(True),
            {
                "id": custom_item.id,
                "user_id": user.id,
                "user": user.__json__(True),
                "anilist": "abc",
                "myanimelist": None,
                "kitsu": None,
                "bakaupdates": None,
                "mangadex": None,
                "vndb": "xyz",
                "anidb": None,
                "animeplanet": None,
                "lndb": None,
                "novelupdates": None,
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_item = \
            AnilistCustomListItem(user=user, anilist="abc", vndb="xyz")
        self.db.session.add(custom_item)
        self.db.session.commit()
        data = custom_item.__json__()
        data.pop("id")
        self.assertEqual(
            str(custom_item),
            "AnilistCustomListItem:{} <{}>".format(custom_item.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_item = \
            AnilistCustomListItem(user=user, anilist="abc", vndb="xyz")
        self.db.session.add(custom_item)
        self.db.session.commit()

        generated = {"value": custom_item}
        code = repr(custom_item)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], custom_item)
        self.assertFalse(generated["value"] is custom_item)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_item = \
            AnilistCustomListItem(user=user, anilist="abc", vndb="xyz")
        custom_item2 = \
            AnilistCustomListItem(user=user, anilist="def", vndb="uvw")
        mapping = {
            custom_item: 100,
            custom_item2: 200
        }
        self.assertEqual(mapping[custom_item], 100)
        self.assertEqual(mapping[custom_item2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_item = \
            AnilistCustomListItem(user=user, anilist="abc", vndb="xyz")
        custom_item1 = \
            AnilistCustomListItem(user=user, anilist="abc", vndb="xyz")
        custom_item2 = \
            AnilistCustomListItem(user=user, anilist="def", vndb="uvw")

        self.assertEqual(custom_item, custom_item)
        self.assertEqual(custom_item, custom_item1)
        self.assertNotEqual(custom_item, custom_item2)
        self.assertNotEqual(custom_item, 100)
