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

from kudubot.Bot import Bot
from kudubot.db.Address import Address
from kudubot.exceptions import ParseError
from bokkichat.entities.message.Message import Message
from bokkichat.entities.message.TextMessage import TextMessage
from aniremind.db.Reminder import Reminder
from aniremind.parsing.AniRemindCommandParser import AniRemindCommandParser


class AniRemindBot(Bot):
    """
    The Aniremind Bot class that defines the anime reminder
    functionality.
    """

    def on_msg(self, message: Message, address: Address):
        """
        Handles received messages
        :param message: The received message
        :param address: The address of the sender in the database
        :return: None
        """
        if not message.is_text():
            return

        message = message  # type: TextMessage
        reply = message.make_reply()  # type: TextMessage
        parser = AniRemindCommandParser()

        try:
            command, args = parser.parse(message.body)
        except ParseError:
            return

        if command == "REGISTER":
            reminder = self.register(args["show_name"], address)
            reply.body = "{} registered".format(reminder)

        elif command == "LIST":
            self.logger.info(
                "Listing reminders for {}".format(address.address)
            )

            reminders = self.db_session.query(Reminder)\
                .filter_by(address=address).all()
            reminders = list(map(lambda x: str(x), reminders))
            reply.body = "\n".join(reminders)

        elif command == "DELETE":
            self.delete(args["id"])
            reply.body = "Reminder #{} was deleted".format(args["id"])

        else:
            return

        self.connection.send(reply)

    def register(self, show_name: str, address: Address) -> Reminder:
        """
        Registers a new show in the reminder
        :param show_name: The name of the show to register
        :param address: The address for which to register the show
        :return: The newly registered reminder object
        """
        self.logger.info(
            "Storing show {} for address {}".format(show_name, address.address)
        )

        reminder = Reminder(address_id=address.id, show_name=show_name)
        self.db_session.add(reminder)
        self.db_session.commit()
        return reminder

    def delete(self, _id: int):
        """
        Deletes a reminder
        :param _id: The ID of the reminder to remove
        :return: None
        """
        self.logger.info("Removing Reminder #{}".format(_id))

        reminder = self.db_session.query(Reminder).filter_by(id=_id).first()
        if reminder is not None:
            self.db_session.delete(reminder)
            self.db_session.commit()
