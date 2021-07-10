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

from otaku_info.external.reddit import load_ln_releases
from otaku_info.test.TestFramework import _TestFramework


class TestReddit(_TestFramework):
    """
    Class that tests the reddit functionality
    """

    def test_retrieving_ln_releases(self):
        """
        Tests retrieving an reddit item
        :return: None
        """
        items = load_ln_releases(2019)
        self.assertGreater(len(items), 0)
        self.assertEqual(
            items[0].series_name,
            "The Master of Ragnarok & Blesser of Einherjar"
        )
