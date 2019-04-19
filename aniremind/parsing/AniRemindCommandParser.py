"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of aniremind.

aniremind is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

aniremind is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with aniremind.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import List
from kudubot.parsing.Command import Command
from kudubot.parsing.CommandParser import CommandParser


class AniRemindCommandParser(CommandParser):
    """
    Parser for the aniremind bot
    """

    @property
    def commands(self) -> List[Command]:
        """
        Defines the commands the parser supports
        :return: The list of commands
        """
        return [
            Command("REGISTER", [("show_name", str)]),
            Command("LIST", []),
            Command("DELETE", [("id", int)])
        ]

    @property
    def name(self) -> str:
        """
        :return: The name of the parser
        """
        return "aniremind"
