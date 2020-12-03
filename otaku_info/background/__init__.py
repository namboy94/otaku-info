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

from typing import Dict, Tuple, Callable
from otaku_info.background.db_inserter import do_inserts
from otaku_info.background.anilist import update_anilist_data
from otaku_info.background.mangadex import update_mangadex_data
from otaku_info.background.manga_chapter_guesses import \
    update_manga_chapter_guesses
from otaku_info.background.notifications import send_new_update_notifications
from otaku_info.background.ln_releases import update_ln_releases


bg_tasks: Dict[str, Tuple[int, Callable]] = {
    "db_inserts": (1, do_inserts),
    "anilist_update": (60 * 5, update_anilist_data),
    "update_manga_chapter_guesses": (60 * 30, update_manga_chapter_guesses),
    "mangadex_update": (60 * 60 * 24, update_mangadex_data),
    "update_notifications": (60, send_new_update_notifications),
    # "ln_release_updates": (60 * 60 * 24, update_ln_releases)
}
"""
A dictionary containing background tasks for the flask application
"""
