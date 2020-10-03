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

from unittest.mock import patch
from jerrycan.db.User import User
from jerrycan.test.mocks import send_email_mock, verify_recaptcha_mock, \
    negative_verify_recaptcha_mock
from otaku_info.test.TestFramework import _TestFramework
from otaku_info.Config import Config


class TestRegisterRoute(_TestFramework):
    """
    Class that tests registration features
    """

    def test_page_get(self):
        """
        Tests getting the page
        :return: None
        """
        resp = self.client.get("/register")
        self.assertTrue(b"<!--user_management/register.html-->" in resp.data)

    def test_registering_user(self):
        """
        Tests registering a new user
        :return: None
        """
        self.assertEqual(len(User.query.all()), 0)
        with self.client:

            with send_email_mock as m:
                with verify_recaptcha_mock:
                    self.assertEqual(0, m.call_count)
                    resp = self.client.post(
                        "/register",
                        follow_redirects=True,
                        data={
                            "username": "testuser",
                            "password": "testpass",
                            "password-repeat": "testpass",
                            "email": "test@example.com",
                            "g-recaptcha-response": ""
                        }
                    )
                    self.assertEqual(1, m.call_count)

            self.assertTrue(b"Registered Successfully" in resp.data)
            self.assertTrue(b"<!--static/index.html-->" in resp.data)
            self.assertEqual(len(User.query.all()), 1)

            user = User.query.filter_by(username="testuser").first()
            self.assertEqual(user.email, "test@example.com")
            self.assertFalse(user.confirmed)

    def test_invalid_registrations(self):
        """
        Tests registering using invalid parameters
        :return: None
        """
        user, _, _ = self.generate_sample_user()
        base = {
            "username": "testuser",
            "password": "testpass",
            "password-repeat": "testpass",
            "email": "test@example.com",
            "g-recaptcha-response": ""
        }
        self.assertEqual(len(User.query.all()), 1)
        with self.client:

            for params in [
                {"password": "testpasses",
                 "expected": b"Passwords do not match"},
                {"username": "-" * (Config.MIN_USERNAME_LENGTH - 1),
                 "expected": b"Username must be between"},
                {"username": "-" * (Config.MAX_USERNAME_LENGTH + 1),
                 "expected": b"Username must be between"},
                {"username": user.username,
                 "expected": b"Username already exists"},
                {"email": user.email,
                 "expected": b"Email already in use"}
            ]:
                data = dict(base)
                data.update(params)

                with send_email_mock as m:
                    self.assertEqual(0, m.call_count)
                    resp = self.client.post(
                        "/register",
                        follow_redirects=True,
                        data=data
                    )
                    self.assertEqual(0, m.call_count)
                self.assertFalse(b"Registered Successfully" in resp.data)
                self.assertTrue(
                    b"<!--user_management/register.html-->" in resp.data
                )
                self.assertTrue(params["expected"] in resp.data)
                self.assertEqual(len(User.query.all()), 1)

    def test_invalid_recaptcha(self):
        """
        Tests that invalid ReCaptcha responses are handled correctly
        :return: None
        """
        with self.client:
            with send_email_mock as m:
                with negative_verify_recaptcha_mock:
                    self.assertEqual(0, m.call_count)
                    resp = self.client.post(
                        "/register",
                        follow_redirects=True,
                        data={
                            "username": "testuser",
                            "password": "testpass",
                            "password-repeat": "testpass",
                            "email": "test@example.com",
                            "g-recaptcha-response": ""
                        }
                    )
                    self.assertEqual(0, m.call_count)

            self.assertFalse(b"Registered Successfully" in resp.data)
            self.assertTrue(b"ReCaptcha not solved correctly" in resp.data)
            self.assertTrue(
                b"<!--user_management/register.html-->" in resp.data
            )
            self.assertEqual(len(User.query.all()), 0)

    def test_confirming(self):
        """
        Tests confirming a user
        :return: None
        """
        user, _, confirm_key = self.generate_sample_user(False)
        with self.client:
            resp = self.client.get("/confirm?user_id={}&confirm_key={}".format(
                user.id, confirm_key
            ), follow_redirects=True)
            self.assertTrue(b"User confirmed successfully" in resp.data)
            self.assertTrue(b"<!--static/index.html-->" in resp.data)
            self.assertTrue(user.confirmed)

    def test_invalid_confirm(self):
        """
        Tests invalid confirmations
        :return: None
        """
        user, _, confirm_key = self.generate_sample_user(False)
        user2, _, confirm_key2 = self.generate_sample_user()
        with self.client:
            for params in [
                {"user_id": "100", "confirm_key": confirm_key,
                 "expected": b"User does not exist"},
                {"user_id": user.id, "confirm_key": "AAA",
                 "expected": b"Confirmation key invalid"},
                {"user_id": user2.id, "confirm_key": confirm_key2,
                 "expected": b"User already confirmed"}
            ]:
                resp = self.client.get(
                    "/confirm?user_id={}&confirm_key={}".format(
                        params["user_id"], params["confirm_key"]
                    ), follow_redirects=True)
                self.assertFalse(b"User confirmed successfully" in resp.data)
                self.assertTrue(b"<!--static/index.html-->" in resp.data)
                self.assertTrue(params["expected"] in resp.data)
                self.assertFalse(user.confirmed)
