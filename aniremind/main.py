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

import os
from kudubot.Bot import Bot
from bokkichat.entities.message.Message import Message
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.connection.Connection import Connection
from bokkichat.connection.impl.TelegramBotConnection import \
    TelegramBotConnection
from bokkichat.settings.impl.TelegramBotSettings import TelegramBotSettings


def main():
    """
    The main method of this program
    :return: None
    """
    config_path = os.path.join(os.path.expanduser("~"), ".config/aniremind")
    settings_file = os.path.join(config_path, "settings.json")

    if not os.path.isfile(settings_file):
        api_key = input("API Key: ")
        settings = TelegramBotSettings(api_key)
        connection = TelegramBotConnection(settings)
        bot = Bot(connection, config_path)
        bot.save_config()

    bot = Bot.load(TelegramBotConnection, config_path)
    bot.start(callback=callback)


def callback(bot: Bot, connection: Connection, message: Message):
    msg = TextMessage(message.receiver, message.sender, str(message))
    connection.send(msg)


if __name__ == "__main__":
    main()
