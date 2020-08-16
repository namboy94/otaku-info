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

from typing import Optional
from otaku_info_web.utils.enums import ListService, MediaType
from otaku_info_web.utils.mappings import list_service_url_formats


def build_service_url(
        media_type: MediaType,
        service: ListService,
        service_id: str
) -> str:
    """
    Builds an URL for an external service based on an ID
    :param media_type: The media type for which to generate an URL
    :param service: The service for which to create the URL
    :param service_id: The ID of the media item on that service
    :return: The generated URL
    """
    url_format = list_service_url_formats[service]
    url = url_format \
        .replace("@{media_type}", media_type.value) \
        .replace("@{id}", service_id)
    return url


def build_title(english_title: Optional[str], romaji_title: str) -> str:
    """
    Determines the title based on an English and Romaji title
    :param english_title: The english title
    :param romaji_title: The romaji title
    :return: The title
    """
    return romaji_title if english_title is None else english_title
