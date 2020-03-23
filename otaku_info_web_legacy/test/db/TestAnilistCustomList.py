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
from otaku_info_web.db.AnilistCustomList import AnilistCustomList


class TestAnilistCustomList(_TestFramework):
    """
    Class that tests anilist custom list database items
    """

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_list = AnilistCustomList(user=user, name="ABC")
        self.db.session.add(custom_list)
        self.db.session.commit()
        self.assertEqual(
            custom_list.__json__(False),
            {
                "id": custom_list.id,
                "user_id": user.id,
                "name": "ABC"
            }
        ),
        self.assertEqual(
            custom_list.__json__(True),
            {
                "id": custom_list.id,
                "user_id": user.id,
                "user": user.__json__(True),
                "name": "ABC"
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_list = AnilistCustomList(user=user, name="abc")
        self.db.session.add(custom_list)
        self.db.session.commit()
        data = custom_list.__json__()
        data.pop("id")
        self.assertEqual(
            str(custom_list),
            "AnilistCustomList:{} <{}>".format(custom_list.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_list = AnilistCustomList(user=user, name="Test")
        self.db.session.add(custom_list)
        self.db.session.commit()

        generated = {"value": custom_list}
        code = repr(custom_list)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], custom_list)
        self.assertFalse(generated["value"] is custom_list)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        user = self.generate_sample_user()[0]
        custom_list = AnilistCustomList(user=user, name="A")
        custom_list2 = AnilistCustomList(user=user, name="B")
        mapping = {
            custom_list: 100,
            custom_list2: 200
        }
        self.assertEqual(mapping[custom_list], 100)
        self.assertEqual(mapping[custom_list2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        user = self.generate_sample_user()[0]
        external = AnilistCustomList(user=user, name="A")
        external1 = AnilistCustomList(user=user, name="A")
        external2 = AnilistCustomList(user=user, name="B")

        self.assertEqual(external, external)
        self.assertEqual(external, external1)
        self.assertNotEqual(external, external2)
        self.assertNotEqual(external, 100)
