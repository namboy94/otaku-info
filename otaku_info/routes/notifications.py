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

from flask import request, render_template, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from puffotter.flask.base import db
from puffotter.flask.db.TelegramChatId import TelegramChatId
from otaku_info.utils.enums import NotificationType
from otaku_info.db.NotificationSetting import NotificationSetting


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
        settings = {
            x: False
            for x in NotificationType
        }
        settings.update({
            x.notification_type: x
            for x in
            NotificationSetting.query.filter_by(user_id=current_user.id).all()
        })
        return render_template(
            "user_management/notifications.html",
            telegram_chat_id=telegram_chat_id,
            notification_settings=settings
        )

    @blueprint.route("/set_notification_settings", methods=["POST"])
    @login_required
    def set_notification_settings():
        """
        Sets the notification settings
        :return: Redirect to notifications page
        """
        existing_settings = {
            x.notification_type: x
            for x in
            NotificationSetting.query.filter_by(user_id=current_user.id).all()
        }
        for notification_type in NotificationType:
            active_input = request.form.get(notification_type.value, "off")
            active_value = active_input == "on"

            min_score_text = request.form.get(
                notification_type.value + "_min_score",
                "0"
            )
            try:
                min_score = int(min_score_text)
            except IndexError:
                min_score = 0

            setting = existing_settings.get(notification_type)
            if setting is None:
                setting = NotificationSetting(
                    user=current_user,
                    notification_type=notification_type,
                    minimum_score=min_score
                )
                db.session.add(setting)

            setting.value = active_value
            setting.minimum_score = min_score
            db.session.commit()

        return redirect(url_for("notifications.notifications"))

    return blueprint
