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

    @classmethod
    def commands(cls) -> List[Command]:
        """
        Defines the commands the parser supports
        :return: The list of commands
        """
        return [
            Command("activate_anime_notifications",
                    [("anilist-username", str)]),
            Command("activate_anime_notifications",
                    [("anilist-username", str), ("custom-list", str)]),
            Command("deactivate_anime_notifications", []),
            Command("list_new_anime_episodes", []),

            Command("activate_manga_notifications",
                    [("anilist-username", str)]),
            Command("activate_manga_notifications",
                    [("anilist-username", str), ("custom-list", str)]),
            Command("deactivate_manga_notifications", []),
            Command("list_new_manga_chapters", []),

            Command("list_ln_releases", []),
            Command("list_ln_releases", [("year", int)]),
            Command("list_ln_releases", [("year", int), ("month", str)]),
        ]

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the parser
        """
        return "otaku_info_bot"
