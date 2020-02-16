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

import os
from base64 import b64encode
from typing import Tuple, Dict
from unittest import TestCase
from puffotter.crypto import generate_random, generate_hash
from otaku_info_web.run import app, db, init
from otaku_info_web.config import Config
from otaku_info_web.db.User import User
from otaku_info_web.db.ApiKey import ApiKey


class _TestFramework(TestCase):
    """
    Class that models a testing framework for the flask application
    """

    def setUp(self):
        """
        Sets up the flask application and a temporary database to test with
        :return: None
        """
        os.environ["FLASK_TESTING"] = "1"

        self.app = app
        self.db = db

        self.app.config["TESTING"] = True
        self.app.secret_key = generate_random(20)
        self.db_path = Config.sqlite_path

        self.cleanup()

        init()
        self.app.app_context().push()

        self.client = self.app.test_client()
        self.context = self.app.test_request_context()

    def tearDown(self):
        """
        Removes any generated files from the filesystem and handles other
        post-test tasks
        :return: None
        """
        self.cleanup()

    def cleanup(self):
        """
        Cleans up the filesystem after/before tests
        :return: None
        """
        try:
            os.remove(self.db_path)
        except FileNotFoundError:
            pass

    def generate_sample_user(self, confirmed: bool = True) \
            -> Tuple[User, str, str]:
        """
        Generates a random user for use in tests
        :param confirmed: Whether or not the user should be confirmed
        :return: The User object, the password and the confirmation key
        """
        password = generate_random(20)
        confirm_key = generate_random(20)
        user = User(
            username=generate_random(12),
            password_hash=generate_hash(password),
            email=generate_random(8) + "@example.com",
            confirmed=confirmed,
            confirmation_hash=generate_hash(confirm_key)
        )
        self.db.session.add(user)
        self.db.session.commit()
        return user, password, confirm_key

    def login_user(self, user: User, password: str):
        """
        Logs in a user
        :param user: The user to log in
        :param password: The password to use
        :return: None
        """
        self.client.post("/login", follow_redirects=True, data={
            "username": user.username,
            "password": password
        })

    def generate_api_key(self, user: User) \
            -> Tuple[ApiKey, str, Dict[str, str]]:
        """
        Generates an API key and base64 encoded headers for requests
        :param user: The user for which to create the key
        :return: The API key object, the actual API key, the headers
        """
        key = generate_random(20)
        hashed = generate_hash(key)
        api_key_obj = ApiKey(user=user, key_hash=hashed)
        self.db.session.add(api_key_obj)
        self.db.session.commit()
        api_key = "{}:{}".format(api_key_obj.id, key)

        return api_key_obj, api_key, self.generate_api_key_headers(api_key)

    # noinspection PyMethodMayBeStatic
    def generate_api_key_headers(self, api_key: str) -> Dict[str, str]:
        """
        Creates HTTP Authorization headers for an API key
        :param api_key: The API key to put in the headers
        :return: The headers
        """
        encoded = b64encode(api_key.encode("utf-8")).decode("utf-8")
        return {
            "Authorization": "Basic {}".format(encoded)
        }
