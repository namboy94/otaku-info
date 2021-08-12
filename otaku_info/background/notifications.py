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

import time
from typing import Dict, List, Tuple
from jerrycan.base import db, app
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.MediaNotification import MediaNotification
from otaku_info.db.NotificationSetting import NotificationSetting
from otaku_info.wrappers.UpdateWrapper import UpdateWrapper
from otaku_info.enums import MediaType, MediaSubType, NotificationType, \
    ConsumingState


def send_new_update_notifications():
    """
    Sends out telegram notifications for media updates
    :return: None
    """
    start = time.time()
    app.logger.info("Starting check for notifications")

    user_states: List[MediaUserState] = MediaUserState.query.filter_by(
        consuming_state=ConsumingState.CURRENT
    ).options(
        db.joinedload(MediaUserState.media_notification)
    ).all()

    notification_settings: Dict[
        Tuple[int, NotificationType],
        NotificationSetting
    ] = {
        (x.user_id, x.notification_type): x
        for x in NotificationSetting.query.all()
    }

    for user_state in user_states:

        target_type = {
            MediaType.ANIME: NotificationType.NEW_ANIME_EPISODES,
            MediaType.MANGA: NotificationType.NEW_MANGA_CHAPTERS
        }.get(user_state.media_type)

        settings = notification_settings.get((
            user_state.user_id, target_type
        ))
        if settings is None or not settings.value:
            continue
        else:
            handle_notification(user_state, settings)

    db.session.commit()
    app.logger.info(f"Completed check for notifications in "
                    f"{time.time() - start}s.")


def handle_notification(
        media_user_state: MediaUserState,
        settings: NotificationSetting
):
    """
    Handles a single notification
    :param media_user_state: The user state for which to notify
    :param settings: The notification settings
    :return: None
    """
    chat = media_user_state.user.telegram_chat_id
    if chat is None:
        return

    update = UpdateWrapper(media_user_state)
    notification = media_user_state.media_notification
    if notification is None:
        notification = MediaNotification(
            service=media_user_state.service,
            service_id=media_user_state.service_id,
            media_type=media_user_state.media_type,
            user_id=media_user_state.user_id,
            last_update=update.latest
        )
        db.session.add(notification)

    if update.diff <= 0:
        return

    if notification.last_update < update.latest:
        notification.last_update = update.latest

        show_update = \
            (update.score is not None
             and update.score >= settings.minimum_score) \
            or settings.minimum_score == 0

        if show_update:
            media_item = media_user_state.media_item
            if media_item.media_type == MediaType.ANIME:
                keyword = "Episode"
            elif media_item.media_subtype == MediaSubType.NOVEL:
                keyword = "Volume"
            else:
                keyword = "Chapter"

            chat.send_message(
                f"New {keyword} for {update.title}\n\n"
                f"{keyword} {update.progress}/{update.latest} "
                f"(+{update.diff})\n\n"
                f"{update.url}"
            )
