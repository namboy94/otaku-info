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

from typing import Dict, List
from puffotter.flask.base import db
from otaku_info_web.db.TelegramChatId import TelegramChatId
from otaku_info_web.db.MediaUserState import MediaUserState
from otaku_info_web.db.MediaNotification import MediaNotification
from otaku_info_web.db.MangaChapterGuess import MangaChapterGuess
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.utils.enums import MediaType, MediaSubType, ConsumingState


def send_new_manga_chapter_notifications():
    """
    Sends out telegram notifications for manga chapter updates
    :return: None
    """

    chats: Dict[int, TelegramChatId] = {
        x.user_id: x for x in TelegramChatId.query.all()
    }
    chapter_guesses: Dict[int, int] = {
        x.media_id_id: x.guess for x in MangaChapterGuess.query.all()
    }
    user_states: List[MediaUserState] = MediaUserState.query\
        .join(MediaId) \
        .join(MediaItem) \
        .filter(MediaItem.media_type == MediaType.MANGA)\
        .filter(MediaItem.media_subtype == MediaSubType.MANGA)\
        .filter(MediaUserState.consuming_state == ConsumingState.CURRENT)\
        .all()
    notifications: Dict[int, MediaNotification] = {
        x.media_user_state_id: x for x in MediaNotification.query.all()
    }

    for user_state in user_states:
        guess = chapter_guesses.get(user_state.media_id_id)
        notification = notifications.get(user_state.id)
        chat = chats.get(user_state.user_id)

        if guess is None or chat is None:
            continue
        if notification is None:
            notification = MediaNotification(
                media_user_state=user_state, last_update=guess
            )
            db.session.add(notification)

        if guess != notification.last_update:
            notification.last_update = guess

            title = user_state.media_id.media_item.title
            url = user_state.media_id.service_url
            chat.send_message(
                f"New Chapter for {title}\n\n"
                f"Chapter {guess}\n\n"
                f"{url}"
            )

    db.session.commit()
