"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-bot.

otaku-info-bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-bot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

import time
from kudubot.db import Base
from sqlalchemy import Column, Integer
from otaku_info_bot.fetching.anilist import guess_latest_manga_chapter


class MangaChapterGuess(Base):
    """
    Models a manga chapter guess
    """

    __tablename__ = "manga_chapter_guesses"
    """
    The name of the database table
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    """
    The anilist ID of the guess
    """

    last_check = Column(Integer, default=0, nullable=False)
    """
    Indicates when the last check was
    """

    guess = Column(Integer, default=0, nullable=False)
    """
    The current guess value
    """

    def update(self) -> bool:
        """
        Updates the current value if more than an hour has elapsed since the
        last update
        :return: Whether or not the value was updated
        """
        if time.time() - self.last_check > 3600:
            self.guess = guess_latest_manga_chapter(self.id)
            self.last_check = time.time()
            return True
        else:
            return False
