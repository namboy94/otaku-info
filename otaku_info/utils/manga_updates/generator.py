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

from typing import List, Tuple, Dict, Any
from puffotter.flask.db.User import User
from puffotter.flask.base import app
from otaku_info.db.MangaChapterGuess import MangaChapterGuess
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaListItem import MediaListItem
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.MediaId import MediaId
from otaku_info.utils.manga_updates.MangaUpdate import MangaUpdate
from otaku_info.utils.db_model_helper import build_title
from otaku_info.utils.enums \
    import MediaType, MediaSubType, ConsumingState, ReleasingState, ListService


def load_applicable_data(
        user: User,
        service: ListService,
        media_list: str,
        include_complete: bool
) -> Tuple[
    Dict[int, Dict[str, Any]],
    Dict[int, Dict[str, Any]],
    Dict[int, Dict[str, Any]],
    Dict[int, Dict[str, Any]],
    Dict[int, Dict[str, Any]],
    Dict[int, int]
]:
    """
    Loads the applicable data from the database in an efficient manner.
    By only loading the data we need and avoiding JOINs, the performance
    is increased drastically.
    Since this method is called for every call to a manga/updates page,
    this should be fast.
    The return values are mostly database IDs mapped to dictionaries
    containing the data required for displaying manga updates.
    A notable exception are the manga chapter guesses, which are simply
    MediaId IDs mapped to the chapter guess value.
    :param user: The user requesting the manga updates
    :param service: The service for which to fetch the updates
    :param media_list: The media list for which to fetch the updates
    :param include_complete: Whether or not to include completed series
    :return: media items, media ids, media user states, media lists,
             media list items, manga chapter guesses
    """

    applicable_releasing_states = [ReleasingState.RELEASING]
    if include_complete:
        applicable_releasing_states += [
            ReleasingState.FINISHED,
            ReleasingState.CANCELLED
        ]

    media_items: Dict[int, Dict[str, Any]] = {
        x[0]: {
            "title": build_title(x[1], x[2]),
            "cover_url": x[3],
            "latest_release": x[4]
        }
        for x in MediaItem.query
        .with_entities(
            MediaItem.id,
            MediaItem.english_title,
            MediaItem.romaji_title,
            MediaItem.cover_url,
            MediaItem.latest_release,
            MediaItem.releasing_state
        )
        .filter(MediaItem.media_type == MediaType.MANGA)
        .filter(MediaItem.media_subtype == MediaSubType.MANGA)
        .all()
        if x[5] in applicable_releasing_states
    }

    media_ids: Dict[int, Dict[str, Any]] = {
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
        if x[1] in media_items
    }

    user_states: Dict[int, Dict[str, Any]] = {
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
            MediaUserState.score,
            MediaUserState.consuming_state
        )
        .all()
        if x[1] in media_ids and x[4] in [
            ConsumingState.CURRENT, ConsumingState.PAUSED
        ]
    }

    user_lists: Dict[int, Dict[str, Any]] = {
        x[0]: {}
        for x in MediaList.query
        .with_entities(MediaList.id)
        .filter_by(user_id=user.id)
        .filter_by(name=media_list)
        .filter_by(service=service)
        .all()
    }

    list_items: Dict[int, Dict[str, Any]] = {
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
        if x[1] in user_lists and x[2] in user_states
    }

    chapter_guesses: Dict[int, int] = {
        x.media_id_id: x.guess
        for x in MangaChapterGuess.query.all()
    }

    return media_items, media_ids, user_states, user_lists, list_items, \
        chapter_guesses


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

    import time
    start = time.time()

    media_items, media_ids, user_states, user_lists, list_items, \
        chapter_guesses = load_applicable_data(
            user, service, media_list, include_complete
        )

    media_item_service_ids: Dict[int, List[Tuple[ListService, str]]] = {
        x: [] for x in media_items
    }
    for _, media_id in media_ids.items():
        media_item_service_ids[media_id["media_item_id"]].append(
            (media_id["service"], media_id["service_id"])
        )

    combined = []
    for media_list_item_id, media_list_item in list_items.items():
        data = media_list_item
        data.update(user_lists[data["media_list_id"]])
        data.update(user_states[data["media_user_state_id"]])
        data.update(media_ids[data["media_id_id"]])
        data.update(media_items[data["media_item_id"]])
        data["guess"] = chapter_guesses.get(data["media_id_id"])

        data["related_ids"] = media_item_service_ids[data["media_item_id"]]

        combined.append(data)

    compiled = [
        MangaUpdate(
            x["media_item_id"],
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

    app.logger.warning(time.time() - start)

    return list(filter(lambda x: x.diff >= min_update_count, compiled))
