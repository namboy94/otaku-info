"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-bot.

otaku-info-bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-bot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import List
from kudubot.parsing.Command import Command
from kudubot.parsing.CommandParser import CommandParser


class OtakuInfoCommandParser(CommandParser):
    """
    Parser for the otaku-info-bot bot
    """

    @property
    def commands(self) -> List[Command]:
        """
        Defines the commands the parser supports
        :return: The list of commands
        """
        return [
            Command("register_anime_reminder", [("show_name", str)]),
            Command("list_anime_reminders", []),
            Command("delete_anime_reminders", [("id", int)]),
            Command("list_ln_releases", []),
            Command("list_ln_releases", [("year", int)]),
            Command("list_ln_releases", [("year", int), ("month", str)])
        ]

    @property
    def name(self) -> str:
        """
        :return: The name of the parser
        """
        return "otaku_info_bot"
