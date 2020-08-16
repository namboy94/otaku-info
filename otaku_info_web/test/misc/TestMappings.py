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

from unittest import TestCase
from otaku_info_web.utils.enums import ListService
from otaku_info_web.utils.mappings import list_service_id_types, \
    list_service_url_formats, mangadex_external_id_names


class TestMappings(TestCase):
    """
    Class that tests enum mappings
    """

    def test_completeness(self):
        """
        Tests that mappings include all possible enum types
        :return: None
        """
        for list_service in ListService:
            self.assertTrue(list_service in list_service_id_types)
            self.assertTrue(list_service in list_service_url_formats)
            self.assertTrue(list_service in mangadex_external_id_names)
