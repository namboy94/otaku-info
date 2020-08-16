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

from typing import Dict, Type
from otaku_info_web.utils.enums import ListService


mangadex_external_id_names: Dict[ListService, str] = {
    ListService.ANILIST: "al",
    ListService.ANIMEPLANET: "ap",
    ListService.KITSU: "kt",
    ListService.MANGAUPDATES: "mu",
    ListService.MYANIMELIST: "mal",
    ListService.MANGADEX: "NONE"
}
"""
The names used by mangadex to identify IDs from other services
"""


list_service_url_formats: Dict[ListService, str] = {
    ListService.ANILIST: "https://anilist.co/@{media_type}/@{id}",
    ListService.ANIMEPLANET: "https://www.anime-planet.com/"
                             "@{media_type}/@{id}",
    ListService.KITSU: "https://kitsu.io/anime/@{id}",
    ListService.MANGAUPDATES: "https://www.mangaupdates.com/"
                              "series.html?id=@{id}",
    ListService.MYANIMELIST: "https://myanimelist.net/@{media_type}/@{id}",
    ListService.MANGADEX: "https://mangadex.org/title/@{id}"
}
"""
Schemas for URLs for external services
"""


list_service_id_types: Dict[ListService, Type] = {
    ListService.ANILIST: int,
    ListService.ANIMEPLANET: str,
    ListService.KITSU: int,
    ListService.MANGAUPDATES: int,
    ListService.MYANIMELIST: int,
    ListService.MANGADEX: int
}
"""
Which type a list service ID should have
"""
