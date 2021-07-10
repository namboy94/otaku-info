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

from otaku_info.external.mangadex import fetch_mangadex_item, add_covers
from otaku_info.test.TestFramework import _TestFramework


class TestMangadex(_TestFramework):
    """
    Class that tests the mangadex functionality
    """

    def test_retrieving_mangadex_item(self):
        """
        Tests retrieving a mangadex item
        :return: None
        """
        item = fetch_mangadex_item("30f3ac69-21b6-45ad-a110-d011b7aaadaa")
        self.assertIsNotNone(item)
        self.assertEqual(item.english_title, "Tonikaku Kawaii")
        self.assertEqual(len(item.cover_url), 36)
        add_covers([item])
        self.assertGreater(len(item.cover_url), 36)
        self.assertTrue(item.cover_url.startswith("http"))
