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
from otaku_info.test.TestFramework import _TestFramework
from otaku_info.main import main


class TestServer(_TestFramework):
    """
    Class that tests starting the server
    """

    def test_starting_server(self):
        """
        Tests starting the server
        :return: None
        """
        class Server:
            def __init__(self, *arg, **kwargs):
                pass

            def start(self):
                raise KeyboardInterrupt()

            def stop(self):
                pass

        def nop(*_, **__):
            pass

        with patch("puffotter.flask.wsgi.Server", Server):
            with patch("puffotter.flask.wsgi.__start_background_tasks", nop):
                main()
