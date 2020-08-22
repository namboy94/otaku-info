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

import traceback
from typing import Dict, Tuple
from sqlalchemy.exc import IntegrityError
from puffotter.flask.base import db, app
from otaku_info.db.ModelMixin import ModelMixin


def update_or_insert_item(
        to_add: ModelMixin,
        existing: Dict[Tuple, ModelMixin],
        commit_updates: bool = False
) -> ModelMixin:
    """
    Updates or creates an item that can be identified based on a unique tuple.
    :param to_add: The item to add
    :param existing: The existing items
    :param commit_updates: Whether or not to commit updates
    :return: None
    """
    existing_item = existing.get(to_add.identifier_tuple)
    try:
        if existing_item is None:
            db.session.add(to_add)
            existing[to_add.identifier_tuple] = to_add
            db.session.commit()
        else:
            existing_item.update(to_add)
            if commit_updates:
                db.session.commit()
    except IntegrityError as e:
        app.logger.error(f"Failed to insert/update: {e}\n"
                         f"{traceback.format_exc()}")
        raise e

    return existing[to_add.identifier_tuple]
