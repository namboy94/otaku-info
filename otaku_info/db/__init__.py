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

from typing import List
from jerrycan.base import db
from otaku_info.db.MangaChapterGuess import MangaChapterGuess
from otaku_info.db.MediaIdMapping import MediaIdMapping
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaList import MediaList
from otaku_info.db.MediaListItem import MediaListItem
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.MediaNotification import MediaNotification
from otaku_info.db.ServiceUsername import ServiceUsername
from otaku_info.db.NotificationSetting import NotificationSetting
from otaku_info.db.LnRelease import LnRelease

models: List[db.Model] = [
    MangaChapterGuess,
    MediaIdMapping,
    MediaItem,
    MediaList,
    MediaListItem,
    MediaUserState,
    ServiceUsername,
    MediaNotification,
    NotificationSetting,
    LnRelease
]
"""
The database models of the application
"""
