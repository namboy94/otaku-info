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

from flask import request, render_template, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from puffotter.flask.base import db
from otaku_info_web.db.TelegramChatId import TelegramChatId


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines a Blueprint that handles notifications for users
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/notifications", methods=["GET"])
    @login_required
    def notifications():
        """
        Displays the notification settings page
        :return: The response
        """
        telegram_chat_id = \
            TelegramChatId.query.filter_by(user=current_user).first()
        return render_template(
            "user_management/notifications.html",
            telegram_chat_id=telegram_chat_id
        )

    @blueprint.route("/set_telegram_chat_id", methods=["POST"])
    @login_required
    def set_telegram_chat_id():
        """
        Sets the Telegram chat ID
        :return: Redirect to notifications page
        """
        chat_id = request.form["telegram_chat_id"]
        db_chat_id = TelegramChatId.query.filter_by(user=current_user).first()

        if db_chat_id is None:
            db_chat_id = TelegramChatId(user=current_user, chat_id=chat_id)
            db.session.add(db_chat_id)
        else:
            db_chat_id.chat_id = chat_id

        db.session.commit()
        return redirect(url_for("notifications.notifications"))

    @blueprint.route(f"/telegram_test", methods=["GET"])
    @login_required
    def telegram_test():
        """
        Can be used to test if telegram messages are sent out correctly
        :return: Redirect to the notifications page
        """
        db_chat_id = TelegramChatId.query.filter_by(user=current_user).first()
        db_chat_id.send_message("Test")
        return redirect(url_for("notifications.notifications"))

    @blueprint.route("/set_notification_settings", methods=["POST"])
    def set_notification_settings():
        return redirect(url_for("notifications.notifications"))

    return blueprint
