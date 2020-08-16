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

from typing import Dict, Any
from puffotter.flask.base import db
from puffotter.flask.db.User import User
from puffotter.flask.db.ModelMixin import ModelMixin
from otaku_info_web.Config import Config
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.entities.Address import Address


class TelegramChatId(ModelMixin, db.Model):
    """
    Database model that stores a telegram chat ID for a user
    """

    __tablename__ = "telegram_chat_ids"
    """
    The name of the database table
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    user_id: int = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
        unique=True
    )
    """
    The ID of the user associated with this telegram chat ID
    """

    user: User = db.relationship(
        "User",
        backref=db.backref(
            "telegram_chat_ids", lazy=True, cascade="all,delete"
        )
    )
    """
    The user associated with this telegram chat ID
    """

    chat_id: str = db.Column(db.String(255), nullable=False)
    """
    The telegram chat ID
    """

    def send_message(self, text: str):
        """
        Sends a message to the chat ID
        :param text: The text to send
        :return: None
        """
        telegram = Config.TELEGRAM_BOT_CONNECTION
        telegram.send(TextMessage(
            telegram.address,
            Address(self.chat_id),
            text
        ))

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models
                                 will be included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "chat_id": self.chat_id
        }
        if include_children:
            data["user"] = self.user.__json__(include_children)
        return data
