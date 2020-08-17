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

MONTHS = [
    "january", "february", "march", "april",
    "may", "june", "july", "august",
    "september", "october", "november", "december"
]


def map_month_name_to_month_number(month_name: str) -> Optional[int]:
    """
    Maps month names to month numbers
    :param month_name: The name of the month
    :return: The month number
    """
    month_name_mapping = {name: i + 1 for i, name in enumerate(MONTHS)}
    return month_name_mapping.get(month_name.lower())


def map_month_number_to_month_name(month_number: int) -> Optional[str]:
    """
    Maps month numbers to month names
    :param month_number: The month number
    :return: The name of the month
    """
    try:
        return MONTHS[month_number - 1]
    except IndexError:
        return None
