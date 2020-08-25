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

from typing import Optional
from threading import get_ident
from typing import Dict, Tuple, Type
from puffotter.flask.base import app
from otaku_info.db.ModelMixin import ModelMixin


class DbCache:
    """
    Class that helps identifying existing items by caching all
    database entries
    """
    __cached: Dict[int, Dict[str, Dict[Tuple, ModelMixin]]] = {}
    """
    This dictionary stores the cached results for each class.
    Attention: This is mapped by class name, so database classes
    must all have unique names (which should be the case anyways).
    The first layer of the dictionary is mapped to thread IDs
    """

    @staticmethod
    def cleanup():
        """
        Removes any cached items for the current thread
        :return: None
        """
        thread_id = get_ident()
        if thread_id in DbCache.__cached:
            DbCache.__cached.pop(thread_id)

    @staticmethod
    def get_existing_item(item: ModelMixin) -> Optional[ModelMixin]:
        """
        Retrieves an existing item from the cache if it exists
        :param item: The item for which to retrieve the existing item
        :return: The existing item or None
        """
        identifier = item.identifier_tuple
        class_name = item.__class__
        class_key = item.__class__.__name__

        existing_items = DbCache.load_existing_items(class_name, False)
        existing_item = existing_items.get(identifier)

        needs_reload = False
        if existing_item is None:
            for other_existing in DbCache.__cached.values():
                others = other_existing.get(class_key, {})
                check = others.get(identifier)

                if check is not None:
                    needs_reload = True
                    break

        if needs_reload:
            existing_items = DbCache.load_existing_items(class_name, True)
            existing_item = existing_items.get(identifier)

        return existing_item

    @staticmethod
    def update_item(item: ModelMixin):
        """
        Updates a cached item
        :param item: The new item
        :return: None
        """
        existing_items = DbCache.load_existing_items(item.__class__, False)
        existing_items[item.identifier_tuple] = item

    @staticmethod
    def load_existing_items(cls: Type[ModelMixin], reload: bool = False) \
            -> Dict[Tuple, ModelMixin]:
        """
        Retrieves all existing items for a database class mapped to their
        identifier tuples.
        Automatically separates the results by thread.
        :param cls: The database class
        :param reload: Whether to force a reload of database data
        :return: The existing entries mapped to identifier tuples
        """
        thread_id = get_ident()
        class_name = cls.__name__

        if thread_id not in DbCache.__cached:
            DbCache.__cached[thread_id] = {}
        thread_cache = DbCache.__cached[thread_id]

        class_cache = thread_cache.get(class_name)
        if class_cache is None:
            thread_cache[class_name] = DbCache.__load(cls)
        elif reload:
            for key in list(class_cache.keys()):
                class_cache.pop(key)
            class_cache.update(DbCache.__load(cls))

        return thread_cache[class_name]

    @staticmethod
    def __load(cls: Type[ModelMixin]) -> Dict[Tuple, ModelMixin]:
        """
        Loads the data for a database class
        :param cls: The database class
        :return: The database data
        """
        app.logger.debug(f"Caching db content for {cls.__name__}")
        # noinspection PyUnresolvedReferences
        return {x.identifier_tuple: x for x in cls.query.all()}
