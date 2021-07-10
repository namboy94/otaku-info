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

from datetime import datetime
from typing import List, Optional
from jerrycan.base import db
from jerrycan.db.User import User
from otaku_info.enums import MediaType, MediaSubType, ListService, \
    ReleasingState
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaListItem import MediaListItem
from otaku_info.db.MediaUserState import MediaUserState


class UpdateWrapper:
    """
    Class that encapsulates important data to display for manga updates
    """

    def __init__(self, media_user_state: MediaUserState):
        """
        Initializes the MangaUpdate object
        :param media_user_state: The media user state contains everything we
                                 need. For performance reasons, it's assumed
                                 that all relations have been loaded already.
        """
        self.user_state = media_user_state
        self.media_item = self.user_state.media_item
        self.title = self.media_item.title
        self.cover_url = self.media_item.cover_url
        self.url = self.media_item.own_url
        self.related_ids = list(self.media_item.ids.values())
        self.related_ids.sort(key=lambda x: x.service.name)

        self.score = self.user_state.score
        self.progress = self.calculate_progress()
        self.latest = self.calculate_latest()

        if self.latest < self.progress:
            self.latest = self.progress

        self.diff = self.latest - self.progress

    def calculate_progress(self) -> int:
        """
        :return: The user's current progress
        """
        media_type = self.media_item.media_type
        subtype = self.media_item.media_subtype
        if media_type == MediaType.MANGA and subtype == MediaSubType.NOVEL:
            progress = self.user_state.volume_progress
        else:
            progress = self.user_state.progress
        if progress is None:
            progress = 0
        return progress

    def calculate_latest(self) -> int:
        """
        :return: The latest release number
        """
        media_type = self.media_item.media_type
        subtype = self.media_item.media_subtype

        if media_type == MediaType.MANGA and subtype == MediaSubType.NOVEL:
            now = datetime.utcnow()
            volumes = [
                x.volume_number
                for x in self.media_item.ln_releases
                if x.release_date < now
            ]
            if len(volumes) == 0:
                latest = self.media_item.latest_volume_release
            else:
                latest = max(volumes)
        elif media_type == MediaType.MANGA:
            chapter_guess = self.media_item.chapter_guess
            if chapter_guess is None:
                latest = self.media_item.latest_release
            else:
                latest = chapter_guess.guess
        elif media_type == MediaType.ANIME \
                and self.media_item.releasing_state == \
                ReleasingState.RELEASING \
                and self.media_item.next_episode is not None:
            latest = max(0, self.media_item.next_episode - 1)
        else:
            latest = self.media_item.latest_release
        if latest is None:
            latest = 0
        return latest

    @classmethod
    def from_media_lists(
            cls,
            media_lists: List[MediaList],
            media_subtype: Optional[MediaSubType],
            minimum_diff: int,
            include_complete: bool
    ) -> List["UpdateWrapper"]:
        """
        Generates UpdateWrapper objects based on media lists
        To avoid huge performance problems, the relations should be fully
        loaded beforehand, preferably in a single query.
        Results can be filtered using the additional parameters
        :param media_lists: The media lists containing the items to wrap
        :param media_subtype: If specified, limits the results to a specific
                              media subtype (example: Light novels)
        :param minimum_diff: Specifies a minimum diff value
        :param include_complete: Specifies whether completed items should be
                                 included
        :return: A list of UpdateWrapper objects
        """
        updates = []
        for media_list in media_lists:
            for list_item in media_list.list_items:
                user_state = list_item.user_state
                media_item = user_state.media_item
                subtype = media_item.media_subtype
                state = media_item.releasing_state
                if not include_complete and state == ReleasingState.FINISHED:
                    continue
                if media_subtype is not None and media_subtype != subtype:
                    continue

                update = cls(user_state)

                if update.diff < minimum_diff:
                    continue

                updates.append(update)

        updates.sort(key=lambda x: 0 if x.score is None else x.score,
                     reverse=True)
        return updates

    @classmethod
    def from_db(
            cls,
            user: User,
            list_name: str,
            service: ListService,
            media_type: MediaType,
            media_subtype: Optional[MediaSubType],
            minimum_diff: int,
            include_complete: bool
    ):
        """
        Generates UpdateWrapper objects based on a couple of parameters
        and the current database contents
        :param user: The user for whom to load the updates
        :param list_name: The list name for which to load the updates
        :param service: The service for which to load the updates
        :param media_type: The media type for which to load the updates
        :param media_subtype: If specified, limits the results to a specific
                              media subtype (example: Light novels)
        :param minimum_diff: Specifies a minimum diff value
        :param include_complete: Specifies whether completed items should be
                                 included
        :return: A list of UpdateWrapper objects
        """
        media_lists: List[MediaList] = MediaList.query \
            .filter_by(
                user=user,
                name=list_name,
                service=service,
                media_type=media_type
            ) \
            .options(
                db.joinedload(MediaList.list_items)
                  .subqueryload(MediaListItem.user_state)
                  .subqueryload(MediaUserState.media_item)
                  .subqueryload(MediaItem.chapter_guess)
            ) \
            .options(
                db.joinedload(MediaList.list_items)
                  .subqueryload(MediaListItem.user_state)
                  .subqueryload(MediaUserState.media_item)
                  .subqueryload(MediaItem.id_mappings)
            ) \
            .options(
                db.joinedload(MediaList.list_items)
                  .subqueryload(MediaListItem.user_state)
                  .subqueryload(MediaUserState.media_item)
                  .subqueryload(MediaItem.ln_releases)
            ) \
            .all()

        return cls.from_media_lists(
            media_lists, media_subtype, minimum_diff, include_complete
        )
