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

from typing import Dict, Tuple, Callable, Any, List
from otaku_info_web.flask import db, app
from otaku_info_web.db.ServiceUsername import ExternalUsername
from otaku_info_web.enums import MediaType
from otaku_info_web.data.anilist import load_anilist
from otaku_info_web.db.User import User
from otaku_info_web.db.MediaItem import AnilistEntry
from otaku_info_web.db.AnilistUserEntry import AnilistUserEntry
from otaku_info_web.db.AnilistCustomList import AnilistCustomList
from otaku_info_web.db.AnilistCustomListItem import AnilistCustomListItem


def update_anilist_entries():
    """
    Updates anilist entries in the database and removes stale entries
    :return: None
    """
    app.logger.info("Updating Anilist Entries")

    anilists = {
        x.user: {MediaType.ANIME: load_anilist(x.anilist, MediaType.ANIME),
                 MediaType.MANGA: load_anilist(x.anilist, MediaType.MANGA)}
        for x in ExternalUsername.query.all()
    }

    all_entries = {MediaType.ANIME: {}, MediaType.MANGA: {}}
    for user, list_data in anilists.items():
        for media_type, lists in list_data.items():
            for list_name, entries in lists.items():
                for entry in entries:
                    anilist_id = entry["media"]["id"]
                    if anilist_id not in all_entries[media_type]:
                        all_entries[media_type][anilist_id] = entry

    entry_id_maps = store_anilist_entries(all_entries)
    user_entry_maps = store_anilist_user_entries(anilists, entry_id_maps)
    list_id_maps = store_custom_lists(anilists)
    store_custom_list_items(anilists, user_entry_maps, list_id_maps)


def store_anilist_entries(
        entries: Dict[MediaType, Dict[int, Dict[str, Any]]]
) -> Dict[MediaType, Dict[int, int]]:
    """
    Stores the anilist entries in the database and updates chapter guesses
    :param entries: The anilist data containing exactly one of each entry
                    to avoid duplicate updates
    :return: A dictionary mapping entry IDs to anilist IDs
    """
    id_mapping = {
        MediaType.MANGA: {},
        MediaType.ANIME: {}
    }
    for media_type, _entries in entries.items():
        for anilist_id, entry in _entries.items():

            media = entry["media"]
            anilist_entry = AnilistEntry.query.filter_by(
                anilist_id=anilist_id,
                media_type=media_type
            ).first()

            if anilist_entry is None:
                anilist_entry = AnilistEntry.from_data(media, media_type)
                db.session.add(anilist_entry)
                db.session.commit()
            else:
                anilist_entry.update(media, media_type)

            anilist_entry.update_chapter_guess()
            db.session.commit()

            id_mapping[media_type][anilist_id] = anilist_entry.id

    return id_mapping


def store_anilist_user_entries(
    anilists: Dict[User, Dict[MediaType, Dict[str, List[Dict[str, Any]]]]],
    id_maps: Dict[MediaType, Dict[int, int]]
) -> Dict[int, Dict[int, int]]:
    """
    Stores anilist user entries in the database and removes any stale ones
    :param anilists: The anilist data
    :param id_maps: Dictionary mapping anilist IDs to entry IDs
    :return: A dictionary mapping user entry ids to anilist ids for each user
    """
    user_entry_maps = {}

    for user, list_data in anilists.items():

        user_entry_maps[user.id] = {}
        existing = {
            x.entry_id: x for x in
            AnilistUserEntry.query.filter_by(user=user).all()
        }

        for media_type, lists in list_data.items():
            for list_name, entries in lists.items():
                for entry in entries:

                    anilist_id = entry["media"]["id"]
                    entry_id = id_maps[media_type][anilist_id]
                    user_entry = existing.get(entry_id)

                    if user_entry is None:
                        user_entry = AnilistUserEntry(
                            user=user, entry_id=entry_id
                        )
                        db.session.add(user_entry)
                    else:
                        existing.pop(entry_id)

                    user_entry.score = entry["score"]
                    user_entry.progress = entry["progress"]

                    db.session.commit()
                    user_entry_maps[user.id][anilist_id] = user_entry.id

        for _, stale_entry in existing.items():
            db.session.delete(stale_entry)
        db.session.commit()

    return user_entry_maps


def store_custom_lists(
    anilists: Dict[User, Dict[MediaType, Dict[str, List[Dict[str, Any]]]]]
) -> Dict[int, Dict[str, int]]:
    """
    Stores the anilist custom user lists in the database and deletes any
    stale ones
    :param anilists: The anilist data
    :return: A dictionary mapping custom list names to their IDs
    """

    list_id_maps = {}

    for user, list_data in anilists.items():

        list_id_maps[user.id] = {}
        user_lists = {
            x.name: x for x in
            AnilistCustomList.query.filter_by(user=user).all()
        }

        for media_type, lists in list_data.items():
            for list_name, _ in lists.items():

                try:
                    custom_list = user_lists.pop(list_name)
                except KeyError:
                    custom_list = AnilistCustomList(user=user, name=list_name)
                    db.session.add(custom_list)
                    db.session.commit()

                list_id_maps[user.id][list_name] = custom_list.id

        for _, stale_list in user_lists.items():
            db.session.delete(stale_list)
        db.session.commit()

    return list_id_maps


def store_custom_list_items(
        anilists: Dict[User, Dict[MediaType, Dict[str, List[Dict[str, Any]]]]],
        user_entry_maps: Dict[int, Dict[int, int]],
        list_id_maps: Dict[int, Dict[str, int]]
):
    """
    Stores custom list items in the database
    :param anilists: The anilist data
    :param user_entry_maps: Anilist IDs mapped to user entry IDs
    :param list_id_maps: Custom list names mapped to their IDs
    :return: None
    """
    for user, list_data in anilists.items():
        for media_type, lists in list_data.items():
            for list_name, entries in lists.items():

                custom_list_id = list_id_maps[user.id][list_name]
                existing_items = {
                    x.user_entry.entry.anilist_id: x for x in
                    AnilistCustomListItem.query.filter_by(
                        custom_list_id=custom_list_id
                    ).all()
                }

                for entry in entries:

                    anilist_id = entry["media"]["id"]
                    user_entry_id = user_entry_maps[user.id][anilist_id]

                    try:
                        existing_items.pop(anilist_id)
                    except KeyError:
                        list_item = AnilistCustomListItem(
                            custom_list_id=custom_list_id,
                            user_entry_id=user_entry_id
                        )
                        db.session.add(list_item)
                        db.session.commit()

                for _, stale_item in existing_items.items():
                    db.session.delete(stale_item)
                db.session.commit()


bg_tasks: Dict[str, Tuple[int, Callable]] = {
    "anilist_entries_update": (5, update_anilist_entries)
}
"""
A dictionary containing background tasks for the flask application
"""
