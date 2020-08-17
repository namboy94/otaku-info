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

from flask.blueprints import Blueprint
from typing import List, Tuple, Callable
from otaku_info.routes.manga import define_blueprint as __manga
from otaku_info.routes.external_service import define_blueprint \
    as __external_service
from otaku_info.routes.api.media_api import define_blueprint as __media_api
from otaku_info.routes.notifications import define_blueprint as \
    __notifications
from otaku_info.routes.media import define_blueprint as __media
from otaku_info.routes.ln import define_blueprint as __ln

blueprint_generators: List[Tuple[Callable[[str], Blueprint], str]] = [
    (__external_service, "external_service"),
    (__manga, "manga"),
    (__media_api, "media_api"),
    (__notifications, "notifications"),
    (__media, "media"),
    (__ln, "ln")
]
"""
Defines the functions used to create the various blueprints
as well as their names
"""
