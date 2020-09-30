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
from jerrycan.base import db
from jerrycan.db.User import User
from sqlalchemy.exc import IntegrityError
from otaku_info.db.ServiceUsername import ServiceUsername
from otaku_info.enums import ListService
from otaku_info.test.TestFramework import _TestFramework


class TestServiceUsername(_TestFramework):
    """
    Class that tests the ServiceUsername database model
    """

    def generate_sample_service_username(self) -> Tuple[ServiceUsername, User]:
        """
        Generates a sample service username
        :return: The service username and the user
        """
        user = self.generate_sample_user(True)[0]
        service_username = ServiceUsername(
            user=user,
            username="abc",
            service=ListService.ANILIST
        )
        db.session.add(service_username)
        db.session.commit()
        return service_username, user

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        service_username, user = self.generate_sample_service_username()

        self.assertEqual(
            service_username.__json__(False),
            {
                "id": service_username.id,
                "user_id": user.id,
                "username": service_username.username,
                "service": service_username.service.value
            }
        )
        self.assertEqual(
            service_username.__json__(True),
            {
                "id": service_username.id,
                "user_id": user.id,
                "user": user.__json__(True),
                "username": service_username.username,
                "service": service_username.service.value
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        service_username, user = self.generate_sample_service_username()
        data = service_username.__json__()
        data.pop("id")
        self.assertEqual(
            str(service_username),
            "ServiceUsername:{} <{}>".format(service_username.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        service_username, user = self.generate_sample_service_username()
        generated = {"value": service_username}
        code = repr(service_username)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], service_username)
        self.assertFalse(generated["value"] is service_username)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        service_username, user = self.generate_sample_service_username()
        service_username_2 = ServiceUsername(
            user=user,
            username="xyz",
            service=ListService.MYANIMELIST
        )
        db.session.add(service_username_2)
        db.session.commit()
        mapping = {
            service_username: 100,
            service_username_2: 200
        }
        self.assertEqual(mapping[service_username], 100)
        self.assertEqual(mapping[service_username_2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        service_username, user = self.generate_sample_service_username()
        service_username_2 = ServiceUsername(
            user=user,
            username="xyz",
            service=ListService.MYANIMELIST
        )
        db.session.add(service_username_2)
        db.session.commit()
        self.assertEqual(service_username, service_username)
        self.assertNotEqual(service_username, service_username_2)
        self.assertNotEqual(service_username, 100)

    def test_uniqueness(self):
        """
        Tests if the uniqueness of the model is handled properly
        :return: None
        """
        service_username, user = self.generate_sample_service_username()

        standard_kwargs = service_username.__json__(False)
        standard_kwargs.pop("id")
        standard_kwargs["service"] = service_username.service

        try:
            duplicate = ServiceUsername(**standard_kwargs)
            db.session.add(duplicate)
            db.session.commit()
            self.fail()
        except IntegrityError:
            db.session.rollback()

        for key, value in [
            ("user_id", self.generate_sample_user()[0].id),
            ("username", "NEW"),
            ("service", ListService.KITSU)
        ]:
            kwargs = dict(standard_kwargs)
            kwargs[key] = value

            generated = ServiceUsername(**kwargs)
            db.session.add(generated)
            db.session.commit()
