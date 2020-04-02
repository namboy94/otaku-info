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
from puffotter.flask.db.User import User
from sqlalchemy.exc import IntegrityError
from otaku_info_web.db.MediaList import MediaList
from otaku_info_web.utils.enums import MediaType, ListService
from otaku_info_web.test.TestFramework import _TestFramework


class TestMediaList(_TestFramework):
    """
    Class that tests the MediaList database model
    """

    def generate_sample_media_list(self) -> Tuple[MediaList, User]:
        """
        Generates a sample media item
        :return: The media list and the associated user
        """
        user = self.generate_sample_user(True)[0]
        media_list = MediaList(
            name="ABC",
            user=user,
            service=ListService.ANILIST,
            media_type=MediaType.MANGA
        )
        db.session.add(media_list)
        db.session.commit()
        return media_list, user

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        media_list, user = self.generate_sample_media_list()

        self.assertEqual(
            media_list.__json__(False),
            {
                "id": media_list.id,
                "name": media_list.name,
                "user_id": user.id,
                "service": media_list.service.value,
                "media_type": media_list.media_type.value
            }
        )
        self.assertEqual(
            media_list.__json__(True),
            {
                "id": media_list.id,
                "name": media_list.name,
                "user_id": user.id,
                "user": user.__json__(True),
                "service": media_list.service.value,
                "media_type": media_list.media_type.value
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        media_list, user = self.generate_sample_media_list()
        data = media_list.__json__()
        data.pop("id")
        self.assertEqual(
            str(media_list),
            "MediaList:{} <{}>".format(media_list.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        media_list, user = self.generate_sample_media_list()
        generated = {"value": media_list}
        code = repr(media_list)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], media_list)
        self.assertFalse(generated["value"] is media_list)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        media_list, user = self.generate_sample_media_list()
        media_list_2 = MediaList(
            name="XYZ",
            user=user,
            service=ListService.ANILIST,
            media_type=MediaType.MANGA
        )
        db.session.add(media_list_2)
        db.session.commit()
        mapping = {
            media_list: 100,
            media_list_2: 200
        }
        self.assertEqual(mapping[media_list], 100)
        self.assertEqual(mapping[media_list_2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        media_list, user = self.generate_sample_media_list()
        media_list_2 = MediaList(
            name="XYZ",
            user=user,
            service=ListService.ANILIST,
            media_type=MediaType.MANGA
        )
        db.session.add(media_list_2)
        db.session.commit()
        self.assertEqual(media_list, media_list)
        self.assertNotEqual(media_list, media_list_2)
        self.assertNotEqual(media_list, 100)

    def test_uniqueness(self):
        """
        Tests if the uniqueness of the model is handled properly
        :return: None
        """
        media_list, user = self.generate_sample_media_list()
        standard_kwargs = media_list.__json__(False)
        standard_kwargs.pop("id")
        standard_kwargs["service"] = media_list.service
        standard_kwargs["media_type"] = media_list.media_type

        try:
            duplicate = MediaList(**standard_kwargs)
            db.session.add(duplicate)
            db.session.commit()
            self.fail()
        except IntegrityError:
            db.session.rollback()

        for key, value in [
            ("name", "ABABABABA"),
            ("user_id", self.generate_sample_user(True)[0].id),
            ("service", ListService.ANIMEPLANET),
            ("media_type", MediaType.ANIME)
        ]:
            kwargs = dict(standard_kwargs)
            kwargs[key] = value

            generated = MediaList(**kwargs)
            db.session.add(generated)
            db.session.commit()
