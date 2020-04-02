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

import json
import requests
from typing import Dict, Optional
from otaku_info_web.utils.enums import ListService
from otaku_info_web.utils.mappings import mangadex_external_id_names, \
    list_service_id_types


def get_external_ids(mangadex_id: int) -> Optional[Dict[ListService, str]]:
    """
    Retrieves associated IDs for a mangadex ID
    :param mangadex_id: The mangadex ID
    :return: The other IDs, mapped to their list service
    """
    endpoint = "https://mangadex.org/api/manga/{}".format(mangadex_id)
    response = json.loads(requests.get(endpoint).text)

    ids = {ListService.MANGADEX: str(mangadex_id)}

    if response["status"] != "OK":
        return None
    else:
        links = response["manga"]["links"]
        if links is None:
            return ids

        for service, identifier in mangadex_external_id_names.items():
            if identifier in links:
                _id = links[identifier]
                id_type = list_service_id_types[service]

                if id_type == int:
                    _id = "".join([x for x in _id if x.isdigit()])

                try:
                    ids[service] = str(id_type(_id))
                except ValueError:
                    pass

    return ids
