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

from typing import List
from puffotter.flask.db.User import User
from puffotter.flask.base import app
from otaku_info_web.db.MangaChapterGuess import MangaChapterGuess
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.db.MediaList import MediaList
from otaku_info_web.db.MediaListItem import MediaListItem
from otaku_info_web.db.MediaUserState import MediaUserState
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.utils.manga_updates.MangaUpdate import MangaUpdate
from otaku_info_web.utils.enums \
    import MediaType, MediaSubType, ConsumingState, ReleasingState, ListService


def prepare_manga_updates(
        user: User,
        service: ListService,
        media_list: str,
        include_complete: bool,
        min_update_count: int
) -> List[MangaUpdate]:
    """
    Prepares easily understandable objects to display for manga updates
    :param user: The user requesting the manga updates
    :param service: The service for which to fetch the updates
    :param media_list: The media list for which to fetch the updates
    :param include_complete: Whether or not to include completed series
    :param min_update_count: The minimum amount of new chapters required
                             for an update to be generated
    :return: A list of MangaUpdate objects, sorted by score
    """
    app.logger.debug("Starting preparing manga updates")

    applicable_releasing_states = [ReleasingState.RELEASING]
    if include_complete:
        applicable_releasing_states += [
            ReleasingState.FINISHED,
            ReleasingState.CANCELLED
        ]

    applicable_media_items = {
        x[0]: {
            "title": x[1] if x[1] is not None else x[2],
            "cover_url": x[3],
            "latest_release": x[4]
        }
        for x in MediaItem.query
        .with_entities(
            MediaItem.id,
            MediaItem.english_title,
            MediaItem.romaji_title,
            MediaItem.cover_url,
            MediaItem.latest_release
        )
        .filter(MediaItem.releasing_state.in_(applicable_releasing_states))
        .filter(MediaItem.media_type == MediaType.MANGA)
        .filter(MediaItem.media_subtype == MediaSubType.MANGA)
        .all()
    }

    applicable_media_ids = {
        x[0]: {
            "media_item_id": x[1],
            "service": x[2],
            "service_id": x[3]
        }
        for x in MediaId.query
        .with_entities(
            MediaId.id,
            MediaId.media_item_id,
            MediaId.service,
            MediaId.service_id
        )
        .all()
        if x[1] in applicable_media_items
    }

    applicable_user_states = {
        x[0]: {
            "media_id_id": x[1],
            "progress": x[2],
            "score": x[3]
        }
        for x in MediaUserState.query
        .with_entities(
            MediaUserState.id,
            MediaUserState.media_id_id,
            MediaUserState.progress,
            MediaUserState.score
        )
        .filter(MediaUserState.consuming_state.in_(
            [ConsumingState.CURRENT, ConsumingState.PAUSED]
        ))
        .all()
        if x[1] in applicable_media_ids
    }

    applicable_user_lists = {
        x[0]: {}
        for x in MediaList.query
        .with_entities(MediaList.id)
        .filter_by(user_id=user.id)
        .filter_by(name=media_list)
        .filter_by(service=service)
        .all()
    }

    applicable_list_items = {
        x[0]: {
            "media_list_id": x[1],
            "media_user_state_id": x[2]
        }
        for x in MediaListItem.query
        .with_entities(
            MediaListItem.id,
            MediaListItem.media_list_id,
            MediaListItem.media_user_state_id
        )
        .all()
        if x[1] in applicable_user_lists and x[2] in applicable_user_states
    }

    applicable_chapter_guesses = {
        x.media_id_id: x.guess
        for x in MangaChapterGuess.query.all()
    }

    media_item_service_ids = {
        x: [] for x in applicable_media_items
    }
    for _, media_id in applicable_media_ids.items():
        media_item_service_ids[media_id["media_item_id"]].append(
            (media_id["service"], media_id["service_id"])
        )

    combined = []
    for media_list_item_id, media_list_item in applicable_list_items.items():
        data = media_list_item
        data.update(applicable_user_lists[data["media_list_id"]])
        data.update(applicable_user_states[data["media_user_state_id"]])
        data.update(applicable_media_ids[data["media_id_id"]])
        data.update(applicable_media_items[data["media_item_id"]])
        data["guess"] = applicable_chapter_guesses.get(data["media_id_id"])

        data["related_ids"] = media_item_service_ids[data["media_item_id"]]

        combined.append(data)

    compiled = [
        MangaUpdate(
            x["title"],
            x["cover_url"],
            x["latest_release"],
            x["progress"],
            x["score"],
            x["guess"],
            x["related_ids"]
        )
        for x in combined
    ]

    return list(filter(lambda x: x.diff >= min_update_count, compiled))
