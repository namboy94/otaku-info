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
from unittest import TestCase
from otaku_info_web.run import app, init


class TestInitialization(TestCase):
    """
    Class that tests the initialization of the flask application
    """

    def test_flask_secret(self):
        """
        Tests if the FLASK_SECRET variable is set correctly
        :return: None
        """
        os.environ["FLASK_TESTING"] = "1"
        os.environ["FLASK_SECRET"] = "ABC"
        init()
        self.assertEqual(app.secret_key, "ABC")
        os.environ.pop("FLASK_SECRET")
        init()
        self.assertNotEqual(app.secret_key, "ABC")
