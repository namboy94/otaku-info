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
from typing import List
from jerrycan.base import db, app
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.MangaChapterGuess import MangaChapterGuess
from otaku_info.enums import MediaType, ListService
from otaku_info.external.anilist import guess_latest_manga_chapter


def update_anilist_manga_chapter_guesses():
    """
    Updates the manga chapter guesses for anilist items
    :return: None
    """
    start = time.time()
    app.logger.info("Starting update of manga chapter guesses")

    guesses: List[MangaChapterGuess] = MangaChapterGuess.query.filter_by(
        service=ListService.ANILIST
    ).all()
    existing_ids = [x.service_id for x in guesses]

    anilist_items: List[MediaUserState] = MediaUserState.query.filter_by(
        service=ListService.ANILIST, media_type=MediaType.MANGA
    ).all()

    for item in anilist_items:
        if item.service_id not in existing_ids:
            new_guess = MangaChapterGuess(
                service=item.service,
                service_id=item.service_id,
                media_type=item.media_type
            )
            new_guess = db.session.merge(new_guess)
            guesses.append(new_guess)
            existing_ids.append(item.service_id)

    db.session.commit()

    for guess in guesses:
        app.logger.debug(f"Updating chapter guess for {guess.service_id}")
        delta = time.time() - guess.last_update
        if delta > 60 * 60:
            guess.last_update = int(time.time())
            guess.guess = guess_latest_manga_chapter(int(guess.service_id))
            db.session.commit()

    app.logger.info(f"Finished updating manga chapter guesses "
                    f"in {time.time() - start}")
