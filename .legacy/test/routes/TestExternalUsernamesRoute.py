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
from otaku_info_web.db.ExternalUsername import ExternalUsername


class TestProfileRoute(_TestFramework):
    """
    Class that tests profile features
    """

    def test_setting_external_usernames(self):
        """
        Tests setting the external usernames, twice.
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        with self.client:
            self.login_user(user, password)
            resp = self.client.post(
                "/external_usernames",
                follow_redirects=True, data={
                    "anilist": "anilist_test_user",
                    "vndb": "visualnovel",
                    "anidb": "",
                    "novelupdates": "ebooks_are_great"
                }
            )
            self.assertTrue(
                b"<!--user_management/profile.html-->" in resp.data
            )
            self.assertTrue(b"anilist_test_user" in resp.data)
            self.assertTrue(b"visualnovel" in resp.data)
            self.assertTrue(b"ebooks_are_great" in resp.data)

            external = ExternalUsername.query.filter_by(user=user).first()
            self.assertEqual(external.anilist, "anilist_test_user")
            self.assertEqual(external.vndb, "visualnovel")
            self.assertEqual(external.novelupdates, "ebooks_are_great")
            self.assertEqual(external.anidb, None)

            resp = self.client.post(
                "/external_usernames",
                follow_redirects=True, data={
                    "anilist": "anilist_test_user",
                    "vndb": "visualnovel",
                    "anidb": "ANIDB has data",
                    "novelupdates": ""
                }
            )
            self.assertTrue(
                b"<!--user_management/profile.html-->" in resp.data
            )
            self.assertTrue(b"anilist_test_user" in resp.data)
            self.assertTrue(b"visualnovel" in resp.data)
            self.assertFalse(b"ebooks_are_great" in resp.data)
            self.assertTrue(b"ANIDB has data" in resp.data)

            external = ExternalUsername.query.filter_by(user=user).first()
            self.assertEqual(external.anilist, "anilist_test_user")
            self.assertEqual(external.vndb, "visualnovel")
            self.assertEqual(external.novelupdates, None)
            self.assertEqual(external.anidb, "ANIDB has data")
