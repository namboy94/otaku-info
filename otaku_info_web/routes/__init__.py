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

from flask.blueprints import Blueprint
from typing import List, Tuple, Callable
from otaku_info_web.routes.manga import define_blueprint as __manga
from otaku_info_web.routes.external_service import define_blueprint \
    as __external_service

blueprint_generators: List[Tuple[Callable[[str], Blueprint], str]] = [
    (__external_service, "external_service"),
    (__manga, "manga")
]
"""
Defines the functions used to create the various blueprints
as well as their names
"""
