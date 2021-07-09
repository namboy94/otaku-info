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
from otaku_info.db.MediaIdMapping import MediaId
from otaku_info.db.MangaChapterGuess import MangaChapterGuess
from otaku_info.enums import MediaType, ListService, MediaSubType


def update_manga_chapter_guesses():
    """
    Updates the manga chapter guesses
    :return: None
    """
    start = time.time()
    app.logger.info("Starting update of manga chapter guesses")

    anilist_ids: List[MediaId] = MediaId.query\
        .filter_by(
            media_type=MediaType.MANGA,
            media_subtype=MediaSubType.MANGA,
            service=ListService.ANILIST
        ) \
        .options(db.joinedload(MediaId.media_user_states)) \
        .options(db.joinedload(MediaId.media_item)) \
        .options(db.joinedload(MediaId.chapter_guess)) \
        .all()

    for anilist_id in anilist_ids:
        if len(anilist_id.media_user_states) == 0:
            # We only update chapter guesses for items that are actively used
            # by users, since each update requires an HTTP request to anilist.
            # We don't want to be rate limited.
            continue
        elif anilist_id.chapter_guess is None:
            new_guess = MangaChapterGuess(media_id=anilist_id)
            db.session.add(new_guess)
            db.session.commit()
            guess = new_guess
        else:
            guess = anilist_id.chapter_guess

        app.logger.debug(f"Updating chapter guess for {anilist_id.service_id}")
        guess.update_guess()
        db.session.commit()

    db.session.commit()
    app.logger.info(f"Finished updating manga chapter guesses "
                    f"in {time.time() - start}")
