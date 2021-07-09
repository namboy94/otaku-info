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
from typing import List, Optional, Dict
from jerrycan.base import app, db
from otaku_info.enums import ListService, MediaType
from otaku_info.utils.object_conversion import anime_list_item_to_media_item, \
    anilist_user_item_to_media_user_state
from otaku_info.db.ServiceUsername import ServiceUsername
from otaku_info.external.anilist import load_anilist
from otaku_info.external.entities.AnilistUserItem import AnilistUserItem


def update_anilist_data(usernames: Optional[List[ServiceUsername]] = None):
    """
    Retrieves all entries on the anilists of all users that provided
    an anilist username
    :param usernames: Can be used to override the usernames to use
    :return: None
    """
    start = time.time()
    app.logger.info("Starting Anilist Update")

    if usernames is None:
        usernames = ServiceUsername.query\
            .filter_by(service=ListService.ANILIST).all()

    from jerrycan.db.User import User
    user = User(username="A", email="A", confirmed=True, confirmation_hash="", password_hash="")
    db.session.add(user)
    s = ServiceUsername(username="namboy94", user=user, service=ListService.ANILIST)
    db.session.add(s)
    db.session.commit()
    usernames = [s]

    ServiceUsername()

    anilist_data: Dict[
        ServiceUsername,
        Dict[MediaType, List[AnilistUserItem]]
    ] = {
        username: {
            media_type: load_anilist(username.username, media_type)
            for media_type in MediaType
        }
        for username in usernames
    }

    for username, anilist_info in anilist_data.items():
        for media_type, anilist_items in anilist_info.items():
            for anilist_item in anilist_items:
                media_item = anime_list_item_to_media_item(anilist_item)
                user_state = anilist_user_item_to_media_user_state(
                    anilist_item, username.user_id
                )
                app.logger.debug(f"Upserting anilist item {media_item.title}")
                db.session.merge(media_item)
                db.session.merge(user_state)

    db.session.commit()
    app.logger.info(f"Finished Anilist Update in {time.time() - start}s.")
