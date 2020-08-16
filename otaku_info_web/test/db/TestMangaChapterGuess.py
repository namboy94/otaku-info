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

from typing import Tuple
from unittest.mock import patch
from puffotter.flask.base import db
from sqlalchemy.exc import IntegrityError
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.db.MangaChapterGuess import MangaChapterGuess
from otaku_info_web.utils.enums import ListService, MediaType, MediaSubType, \
    ReleasingState
from otaku_info_web.test.TestFramework import _TestFramework


class TestMangaChapterGuess(_TestFramework):
    """
    Class that tests the MangaChapterGuess database model
    """

    @staticmethod
    def generate_sample_guess() \
            -> Tuple[MediaItem, MediaId, MangaChapterGuess]:
        """
        Generates a sample chapter guess
        :return: The media item, media id and chapter guess
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
            service_id="101177",
            service=ListService.ANILIST
        )
        chapter_guess = MangaChapterGuess(
            media_id=media_id,
            guess=None,
            last_update=0
        )
        db.session.add(media_item)
        db.session.add(media_id)
        db.session.add(chapter_guess)
        db.session.commit()
        return media_item, media_id, chapter_guess

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        _, media_id, chapter_guess = self.generate_sample_guess()

        self.assertEqual(
            chapter_guess.__json__(False),
            {
                "id": chapter_guess.id,
                "media_id_id": media_id.id,
                "guess": chapter_guess.guess,
                "last_update": chapter_guess.last_update
            }
        )
        self.assertEqual(
            chapter_guess.__json__(True),
            {
                "id": chapter_guess.id,
                "media_id": media_id.__json__(True),
                "media_id_id": media_id.id,
                "guess": chapter_guess.guess,
                "last_update": chapter_guess.last_update
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        media_item, media_id, chapter_guess = self.generate_sample_guess()
        data = chapter_guess.__json__()
        data.pop("id")
        self.assertEqual(
            str(chapter_guess),
            "MangaChapterGuess:{} <{}>".format(chapter_guess.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        _, __, chapter_guess = self.generate_sample_guess()
        generated = {"value": chapter_guess}
        code = repr(chapter_guess)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], chapter_guess)
        self.assertFalse(generated["value"] is chapter_guess)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        media_item, media_id, chapter_guess = self.generate_sample_guess()

        media_id_kwargs = media_id.__json__(False)
        media_id_kwargs.pop("id")
        media_id_kwargs["service"] = ListService.ANIMEPLANET
        new_media_id = MediaId(**media_id_kwargs)
        db.session.add(new_media_id)
        db.session.commit()

        chapter_guess_2 = MangaChapterGuess(
            media_id=new_media_id,
            guess=100,
            last_update=0
        )
        db.session.add(chapter_guess_2)
        db.session.commit()
        mapping = {
            chapter_guess: 100,
            chapter_guess_2: 200
        }
        self.assertEqual(mapping[chapter_guess], 100)
        self.assertEqual(mapping[chapter_guess_2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        _, media_id, chapter_guess = self.generate_sample_guess()

        media_id_kwargs = media_id.__json__(False)
        media_id_kwargs.pop("id")
        media_id_kwargs["service"] = ListService.ANIMEPLANET
        new_media_id = MediaId(**media_id_kwargs)
        db.session.add(new_media_id)
        db.session.commit()

        chapter_guess_2 = MangaChapterGuess(
            media_id=new_media_id,
            guess=100,
            last_update=0
        )
        self.assertEqual(chapter_guess, chapter_guess)
        self.assertNotEqual(chapter_guess, chapter_guess_2)
        self.assertNotEqual(chapter_guess, 100)

    def test_guessing_latest_chapter(self):
        """
        Tests guessing the latest chapter
        :return: None
        """
        _, _, chapter_guess = self.generate_sample_guess()

        with patch("otaku_info_web.db.MangaChapterGuess"
                   ".guess_latest_manga_chapter", lambda _: 105):
            self.assertEqual(chapter_guess.guess, None)
            self.assertEqual(chapter_guess.last_update, 0)
            chapter_guess.update()
            self.assertEqual(chapter_guess.guess, 105)
            self.assertGreater(chapter_guess.last_update, 0)
            chapter_guess.guess = 77
            last_update = chapter_guess.last_update
            chapter_guess.update()
            self.assertEqual(chapter_guess.guess, 77)
            self.assertEqual(chapter_guess.last_update, last_update)
            chapter_guess.last_update = 0
            chapter_guess.update()
            self.assertEqual(chapter_guess.guess, 105)
            self.assertGreaterEqual(chapter_guess.last_update, last_update)

    def test_uniqueness(self):
        """
        Tests if the uniqueness of the model is handled properly
        :return: None
        """
        _, media_id, chapter_guess = self.generate_sample_guess()
        duplicate = MangaChapterGuess(
            media_id_id=media_id.id,
            guess=12345,
            last_update=12345
        )
        try:
            db.session.add(duplicate)
            db.session.commit()
            self.fail()
        except IntegrityError:
            pass
