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


class TestAnilistCustomList(_TestFramework):
    """
    Class that tests anilist user entry database items
    """

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        external = ExternalUsername(user=user, anilist="abc", vndb="xyz")
        self.db.session.add(external)
        self.db.session.commit()
        self.assertEqual(
            external.__json__(False),
            {
                "id": external.id,
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
            external.__json__(True),
            {
                "id": external.id,
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
        external = ExternalUsername(user=user, anilist="abc", vndb="xyz")
        self.db.session.add(external)
        self.db.session.commit()
        data = external.__json__()
        data.pop("id")
        self.assertEqual(
            str(external),
            "ExternalUsername:{} <{}>".format(external.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        user = self.generate_sample_user()[0]
        external = ExternalUsername(user=user, anilist="abc", vndb="xyz")
        self.db.session.add(external)
        self.db.session.commit()

        generated = {"value": external}
        code = repr(external)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], external)
        self.assertFalse(generated["value"] is external)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        user = self.generate_sample_user()[0]
        external = ExternalUsername(user=user, anilist="abc", vndb="xyz")
        external2 = ExternalUsername(user=user, anilist="def", vndb="uvw")
        mapping = {
            external: 100,
            external2: 200
        }
        self.assertEqual(mapping[external], 100)
        self.assertEqual(mapping[external2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        user = self.generate_sample_user()[0]
        external = ExternalUsername(user=user, anilist="abc", vndb="xyz")
        external1 = ExternalUsername(user=user, anilist="abc", vndb="xyz")
        external2 = ExternalUsername(user=user, anilist="def", vndb="uvw")

        self.assertEqual(external, external)
        self.assertEqual(external, external1)
        self.assertNotEqual(external, external2)
        self.assertNotEqual(external, 100)
