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
from otaku_info.db.LnRelease import LnRelease
from otaku_info.enums import ListService, MediaType


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

    __ln_release_queue: List[Tuple[
        Dict[str, Any],
        Dict[ListService, str],
    ]] = []
    """
    Queue for light novel releases
    See queue_ln_release for information of the parts
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
    def queue_ln_release(
            ln_params: Dict[str, Any],
            service_ids: Dict[ListService, str],
    ):
        """
        Queues an LN release
        :param ln_params: The parameters for the LN release
        :param service_ids: Any associated IDs
        :return: None
        """
        with DbQueue.queue_lock:
            DbQueue.__ln_release_queue.append((ln_params, service_ids))

    @staticmethod
    def process_queue():
        """
        Processes all queues
        :return: None
        """
        try:
            DbQueue.queue_lock.acquire()

            # Prepare existing DB content
            media_items: Dict[Tuple, MediaItem] = {
                x.identifier_tuple: x for x in
                MediaItem.query
                .options(db.joinedload(MediaItem.media_ids))
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
            ln_releases: Dict[Tuple, LnRelease] = {
                x.identifier_tuple: x for x in
                LnRelease.query.all()
            }

            media_item_mapped_ids: Dict[int, Dict[ListService, MediaId]] = {
                x.id: {
                    y.service: y for y in x.media_ids
                } for x in media_items.values()
            }

            DbQueue.__process_media_items(
                media_items, media_ids, media_lists, media_item_mapped_ids
            )
            DbQueue.__process_ln_releases(
                ln_releases, media_ids
            )
            db.session.commit()
        finally:
            DbQueue.queue_lock.release()

    @staticmethod
    def __process_media_items(
            media_items: Dict[Tuple, MediaItem],
            media_ids: Dict[Tuple, MediaId],
            media_lists: Dict[Tuple, MediaList],
            media_item_mapped_ids: Dict[int, Dict[ListService, MediaId]]
    ):

        while len(DbQueue.__media_item_queue) > 0:
            params, service, service_ids, user_state_params, list_params = \
                DbQueue.__media_item_queue.pop(0)

            service_id = service_ids.get(service)
            if service_id is None:
                app.logger.error(f"Missing service ID for service {service}")
                continue

            media_type = params["media_type"]
            app.logger.debug(
                f"Inserting media item '{params['romaji_title']}' "
                f"into database"
            )

            media_item = DbQueue.__insert_media_item(
                params,
                media_type,
                service,
                service_ids,
                media_items,
                media_ids,
                media_item_mapped_ids
            )
            media_id = DbQueue.__insert_media_ids(
                media_item,
                service,
                service_ids,
                media_ids,
                media_item_mapped_ids
            )

            # Insert User States
            if user_state_params is not None:
                user_state = DbQueue.__insert_user_state(
                    user_state_params,
                    media_id
                )

                if list_params is not None:
                    DbQueue.__insert_media_list(
                        user_state,
                        list_params,
                        media_lists
                    )

    @staticmethod
    def __process_ln_releases(
            ln_releases: Dict[Tuple, LnRelease],
            media_ids: Dict[Tuple, MediaId]
    ):
        """
        Adds and/or updates light novel releases
        :param ln_releases: Existing light novel releases
        :param media_ids: Existing media IDs
        :return: None
        """
        while len(DbQueue.__ln_release_queue) > 0:
            params, ids = DbQueue.__ln_release_queue.pop(0)

            app.logger.debug(
                f"Inserting ln release "
                f"'{params['series_name']} volume {params['volume']}' "
                f"into database"
            )

            if len(ids) > 0:
                ref_service, ref_id = list(ids.items())[0]
                id_identifier = (MediaType.MANGA, ref_service, ref_id)
                media_id = media_ids.get(id_identifier)
                if media_id is not None:
                    params["media_item_id"] = media_id.media_item_id

            identifier = (
                params["series_name"],
                params["volume"],
                params["digital"],
                params["physical"]
            )
            release = ln_releases.get(identifier)
            if release is None:
                release = LnRelease(**params)
                db.session.add(release)
                db.session.commit()
                ln_releases[release.identifier_tuple] = release
            else:
                if release.media_item_id is None:
                    print(params)
                print(release.media_item_id)
                release.update(LnRelease(**params))
                print(release.media_item_id)

    @staticmethod
    def __insert_media_item(
            params: Dict[str, Any],
            media_type: MediaType,
            base_service: ListService,
            service_ids: Dict[ListService, str],
            media_items: Dict[Tuple, MediaItem],
            media_ids: Dict[Tuple, MediaId],
            media_item_mapped_ids: Dict[int, Dict[ListService, MediaId]]
    ) -> MediaItem:
        """
        Inserts or updates media items
        :param params: The constructor parameters for the MediaItem object
        :param media_type: The media type
        :param base_service: The base service
        :param service_ids: The service IDs
        :param media_items: Cached media items
        :param media_ids: Cached media IDs
        :param media_item_mapped_ids: Service IDs mapped to media item IDs
        :return: The MediaItem object
        """
        id_tuple = (media_type, base_service, service_ids[base_service])
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
                db.session.commit()
                media_items[media_item.identifier_tuple] = media_item
                media_item_mapped_ids[media_item.id] = {
                    x.service: x for x in media_item.media_ids
                }
            else:
                media_item = existing
                identifier = media_item.identifier_tuple
                media_item.update(generated)
                new_identifier = media_item.identifier_tuple
                if identifier != new_identifier:
                    db.session.commit()
                    media_items.pop(identifier)
                    media_items[new_identifier] = media_item

        return media_item

    @staticmethod
    def __insert_media_ids(
            media_item: MediaItem,
            base_service: ListService,
            service_ids: Dict[ListService, str],
            media_ids: Dict[Tuple, MediaId],
            media_item_mapped_ids: Dict[int, Dict[ListService, MediaId]]
    ) -> MediaId:
        """
        Inserts/Updates media IDs
        :param media_item: The associated MediaItem object
        :param base_service: The base service
        :param service_ids: The service IDs
        :param media_ids: Cached media IDs
        :param media_item_mapped_ids: Service IDs mapped to media item IDs
        :return: The MediaID object associated with the base service
        """
        existing_ids = media_item_mapped_ids[media_item.id]
        for service, service_id in service_ids.items():

            id_tuple = (media_item.media_type, service, service_id)
            associated = media_ids.get(id_tuple)

            if associated is None:
                associated = existing_ids.get(service)

            if associated is None:
                media_id = MediaId(
                    media_item=media_item,
                    service=service,
                    service_id=service_id
                )
                db.session.add(media_id)
                db.session.commit()
                media_ids[media_id.identifier_tuple] = media_id
                media_item_mapped_ids[media_item.id][service] = media_id

            elif associated.media_item_id != media_item.id:
                associated.media_item_id = media_item.id
                db.session.commit()

        return media_item_mapped_ids[media_item.id][base_service]

    @staticmethod
    def __insert_user_state(
            params: Dict[str, Any],
            media_id: MediaId
    ) -> MediaUserState:
        """
        Inserts/Updates a user state
        :param params: The parameters for the user state
        :param media_id: The associated media ID
        :return: The user state
        """
        params["media_id_id"] = media_id.id
        generated = MediaUserState(**params)
        existing_user_states = {
            x.user_id: x for x in media_id.media_user_states
        }
        user_id = params["user_id"]
        existing_user_state = existing_user_states.get(user_id)

        if existing_user_state is None:
            db.session.add(generated)
            user_state = generated
            db.session.commit()
        else:
            existing_user_state.update(generated)
            user_state = existing_user_state

        return user_state

    @staticmethod
    def __insert_media_list(
            user_state: MediaUserState,
            params: Dict[str, Any],
            media_lists: Dict[Tuple, MediaList]
    ) -> MediaList:
        """
        Inserts/Updates a media list and associated list entry
        :param user_state: The user state that's part of the list
        :param params: Parameters for the list constructor
        :param media_lists: Cached media lists
        :return: The media list
        """
        generated = MediaList(**params)
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

        return media_list
