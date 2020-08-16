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
from otaku_info.utils.anilist.api import load_anilist, \
    guess_latest_manga_chapter, load_media_info
from otaku_info.utils.enums import MediaType


class TestApi(_TestFramework):
    """
    Class that tests the anilist API functions
    """

    def test_loading_anilist(self):
        """
        Tests loading a user's anilist
        :return: None
        """
        load_anilist("namboy94", MediaType.MANGA)
        load_anilist("namboy94", MediaType.ANIME)

    def test_guessing_manga_chapter(self):
        """
        Tests guessing a manga chapter
        :return: None
        """
        guess = guess_latest_manga_chapter(101177)
        self.assertGreater(guess, 100)

    def test_loading_media(self):
        """
        Tests loading a media item
        :return: None
        """
        media = load_media_info(1, MediaType.ANIME)
        self.assertEqual(media.english_title, "Cowboy Bebop")
        self.assertGreater(len(media.relations), 0)
