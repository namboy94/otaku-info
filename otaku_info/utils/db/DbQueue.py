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

from threading import Lock
from jerrycan.base import db, app
from typing import List, Dict, Any, Tuple, Optional
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaId import MediaId
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaListItem import MediaListItem
from otaku_info.enums import ListService


class DbQueue:
    """
    Class that handles database entry queues
    This is needed to avoid conflicts due to multi-threaded workflows
    """

    queue_lock = Lock()
    """
    Lock used while inserting and removing entries from the queue to avoid
    thread-related problems
    """

    __media_item_queue: List[Tuple[
        Dict[str, Any],
        ListService,
        Dict[ListService, str],
        Optional[Dict[str, Any]],
        Optional[Dict[str, Any]]
    ]] = []
    """
    Queue for new media items. Can contain additional information like
    list entries etc. See the queue_media_item method for more information
    """

    @staticmethod
    def queue_media_item(
            params: Dict[str, Any],
            base_service: ListService,
            service_ids: Dict[ListService, str],
            media_user_state_params: Optional[Dict[str, Any]] = None,
            media_list_params: Optional[Dict[str, Any]] = None
    ):
        """
        Enqueues a media item to insert
        :param params: The parameters for the media item
        :param base_service: The service on which to base the media item
        :param service_ids: The available service IDs
        :param media_user_state_params: The media user state parameters,
                                        if available
        :param media_list_params: The media list parameters, if available
        :return: None
        """
        with DbQueue.queue_lock:
            DbQueue.__media_item_queue.append((
                params,
                base_service,
                service_ids,
                media_user_state_params,
                media_list_params
            ))

    @staticmethod
    def process_queue():
        """
        Processes all queues
        :return: None
        """
        with DbQueue.queue_lock:

            # Prepare existing DB content
            media_items: Dict[Tuple, MediaItem] = {
                x.identifier_tuple: x for x in
                MediaItem.query
                .all()
            }
            media_ids: Dict[Tuple, MediaId] = {
                x.identifier_tuple: x for x in
                MediaId.query
                .options(db.joinedload(MediaId.media_item))
                .options(db.joinedload(MediaId.media_user_states))
                .all()
            }
            media_lists: Dict[Tuple, MediaList] = {
                x.identifier_tuple: x for x in
                MediaList.query
                .options(db.joinedload(MediaList.media_list_items))
                .all()
            }

            DbQueue.__process_media_items(media_items, media_ids, media_lists)

    @staticmethod
    def __process_media_items(
            media_items: Dict[Tuple, MediaItem],
            media_ids: Dict[Tuple, MediaId],
            media_lists: Dict[Tuple, MediaList]
    ):
        """
        Processes all media items in the queue
        :return: None
        """
        while len(DbQueue.__media_item_queue) > 0:
            params, service, service_ids, user_state_params, list_params = \
                DbQueue.__media_item_queue.pop(0)

            service_id = service_ids.get(service)
            if service_id is None:
                app.logger.error(f"Missing service ID for service {service}")
                continue

            media_type = params["media_type"]
            app.logger.debug(
                f"Inserting {params['romaji_title']} into database")

            # Check if media item already exists
            id_tuple = (media_type, service, service_id)
            anchor_id = media_ids.get(id_tuple)
            if anchor_id is None:
                for alt_service, alt_id in service_ids.items():
                    alt_id_tuple = (media_type, alt_service, alt_id)
                    if alt_id_tuple in media_ids:
                        anchor_id = media_ids[alt_id_tuple]

            if anchor_id is not None:
                media_item = anchor_id.media_item
                media_item.update(MediaItem(**params))
            else:
                generated = MediaItem(**params)
                item_identifier = generated.identifier_tuple
                existing = media_items.get(item_identifier)
                if existing is None:
                    media_item = generated
                    db.session.add(media_item)
                    media_items[media_item.identifier_tuple] = media_item
                else:
                    media_item = existing
                    media_item.update(generated)

            # Insert Media IDs
            for alt_service, alt_id in service_ids.items():

                alt_tuple = (media_type, alt_service, alt_id)
                associated = media_ids.get(alt_tuple)

                if associated is None:
                    media_id = MediaId(
                        media_item=media_item,
                        service=alt_service,
                        service_id=alt_id
                    )
                    db.session.add(media_id)
                    db.session.commit()
                    media_ids[media_id.identifier_tuple] = media_id

                elif associated.media_item.id != media_item.id:
                    associated.media_item_id = media_item.id

            # Insert User States
            if user_state_params is not None:
                media_id = media_ids[id_tuple]
                user_state_params["media_id_id"] = media_id.id
                generated = MediaUserState(**user_state_params)
                existing_user_states = {
                    x.user_id: x for x in media_id.media_user_states
                }
                user_id = user_state_params["user_id"]
                existing_user_state = existing_user_states.get(user_id)

                if existing_user_state is None:
                    db.session.add(generated)
                    user_state = generated
                    db.session.commit()
                else:
                    existing_user_state.update(generated)
                    user_state = existing_user_state

                if list_params is not None:
                    generated = MediaList(**list_params)
                    list_identifier = generated.identifier_tuple
                    existing_list = media_lists.get(list_identifier)

                    if existing_list is None:
                        db.session.add(generated)
                        db.session.commit()
                        media_list = generated
                        media_lists[list_identifier] = media_list
                    else:
                        existing_list.update(generated)
                        media_list = existing_list

                    media_list_item_ids = [
                        x.media_user_state_id for x in
                        media_list.media_list_items
                    ]
                    if user_state.id not in media_list_item_ids:
                        list_item = MediaListItem(
                            media_list_id=media_list.id,
                            media_user_state_id=user_state.id
                        )
                        db.session.add(list_item)
