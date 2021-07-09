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

from flask import url_for
from otaku_info.enums import ListService, MediaType
from otaku_info.mappings import list_service_url_formats


def generate_service_url(
        service: ListService,
        media_type: MediaType,
        service_id: str
) -> str:
    """
    :return: The URL to the series for the given service
    """
    url_format = list_service_url_formats[service]
    url = url_format \
        .replace("@{media_type}", f"{media_type.value}") \
        .replace("@{id}", service_id)
    return url


def generate_service_icon_url(service: ListService) -> str:
    """
    :return: The path to the service's icon file
    """
    return url_for(
        "static",
        filename=f"images/service_logos/{service.value}.png"
    )
