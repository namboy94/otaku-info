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

from typing import List, Dict
from puffotter.flask.db.User import User
from otaku_info_web.db.MangaChapterGuess import MangaChapterGuess
from otaku_info_web.db.MediaListItem import MediaListItem
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.utils.manga_updates.MangaUpdate import MangaUpdate
from otaku_info_web.utils.enums \
    import MediaType, ListService, ConsumingState, ReleasingState


def prepare_manga_updates(
        user: User,
        service: str,
        media_list: str,
        include_complete: bool,
        only_updates: bool
) -> List[MangaUpdate]:
    """
    Prepares easily understandable objects to display for manga updates
    :param user: The user requesting the manga updates
    :param service: The service for which to fetch the updates
    :param media_list: The media list for which to fetch the updates
    :param include_complete: Whether or not to include completed series
    :param only_updates: Whether or not to only retrieve entries with at least
                         one new chapter
    :return: A list of MangaUpdate objects, sorted by score
    """
    all_ids = MediaId.query.all()

    list_items: Dict[int, MediaListItem] = {
        x.media_user_state.media_id.service_id: x
        for x in MediaListItem.query.all()
        if x.media_list.name == media_list
        and x.media_list.user.id == user.id
        and x.media_list.service == ListService(service)
        and x.media_user_state.media_id.media_item.media_type
        == MediaType.MANGA
    }
    chapter_guesses = {
        x.media_id.service_id: x
        for x in MangaChapterGuess.query.all()
        if x.media_id.service_id in list_items
    }

    manga_updates: List[MangaUpdate] = []
    for service_id, list_item in list_items.items():

        if list_item.media_user_state.consuming_state not in [
            ConsumingState.CURRENT, ConsumingState.PAUSED
        ]:
            continue

        releasing_state = \
            list_item.media_user_state.media_id.media_item.releasing_state
        applicable_releasing_states = [ReleasingState.RELEASING]
        if include_complete:
            applicable_releasing_states += [
                ReleasingState.FINISHED,
                ReleasingState.CANCELLED
            ]
        if releasing_state not in applicable_releasing_states:
            continue

        chapter_guess = chapter_guesses.get(service_id)

        media_item_id = list_item.media_user_state.media_id.media_item_id
        entry_ids = {
            x.service: x for x in all_ids if x.media_item_id == media_item_id
        }

        update = MangaUpdate(list_item, chapter_guess, entry_ids)

        if only_updates and update.diff == 0:
            continue

        manga_updates.append(update)

    manga_updates.sort(key=lambda x: x.score, reverse=True)
    return manga_updates
