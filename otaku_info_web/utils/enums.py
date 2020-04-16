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

from enum import Enum


class MediaType(Enum):
    """
    Class that models a media type for media items
    """
    ANIME = "anime"
    MANGA = "manga"


class MediaSubType(Enum):
    """
    Class that models a media subtype for media items
    """
    TV = "tv"
    TV_SHORT = "tv_short"
    MOVIE = "movie"
    SPECIAL = "special"
    OVA = "ova"
    ONA = "ona"
    MUSIC = "music"
    MANGA = "manga"
    NOVEL = "novel"
    ONE_SHOT = "one_shot"
    UNKNOWN = "unknown"


class MediaRelationType(Enum):
    """
    Class that models a media relation type
    """
    ADAPTATION = "adaptation"
    PREQUEL = "prequel"
    SEQUEL = "sequel"
    PARENT = "parent"
    SIDE_STORY = "side_story"
    CHARACTER = "character"
    SUMMARY = "summary"
    ALTERNATIVE = "alternative"
    SPIN_OFF = "spin_off"
    OTHER = "other"
    SOURCE = "source"
    COMPILATION = "compilation"
    CONTAINS = "contains"


class ListService(Enum):
    """
    Class that defines available list services
    """
    ANILIST = "anilist"
    MYANIMELIST = "myanimelist"
    MANGADEX = "mangadex"
    MANGAUPDATES = "mangaupdates"
    KITSU = "kitsu"
    ANIMEPLANET = "animeplanet"


class ReleasingState(Enum):
    """
    Class that defines possible releasing states
    """
    FINISHED = "finished"
    RELEASING = "releasing"
    NOT_YET_RELEASED = "not_yet_released"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ConsumingState(Enum):
    """
    Class that defines the possible consuming states for a user and media item
    """
    CURRENT = "current"
    PLANNING = "planning"
    COMPLETED = "completed"
    DROPPED = "dropped"
    PAUSED = "paused"
    REPEATING = "repeating"
