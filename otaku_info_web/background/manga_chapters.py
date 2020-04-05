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

import time
from puffotter.flask.base import db, app
from otaku_info_web.db.MediaUserState import MediaUserState
from otaku_info_web.db.MangaChapterGuess import MangaChapterGuess
from otaku_info_web.utils.enums import MediaType, ListService


def update_manga_chapter_guesses():
    """
    Updates the manga chapter guesses
    :return: None
    """
    app.logger.info("Starting update of manga chapter guesses")
    anilist_ids = {
        x.media_id.service_id: x.media_id
        for x in MediaUserState.query.all()
        if x.media_id.media_item.media_type == MediaType.MANGA
        and x.media_id.service == ListService.ANILIST
    }
    guesses = {
        x.media_id.service_id: x
        for x in MangaChapterGuess.query.all()
    }

    for anilist_id in anilist_ids:
        if anilist_id not in guesses:
            new_guess = MangaChapterGuess(media_id=anilist_ids[anilist_id])
            db.session.add(new_guess)
            guesses[anilist_id] = new_guess

    db.session.commit()

    for anilist_id, guess in guesses.items():

        if anilist_id not in anilist_ids:
            db.session.delete(guess)
            app.logger.debug(f"Deleting stale chapter guess for {anilist_id}")
        else:
            app.logger.debug(f"Updating chapter guess for {anilist_id}")
            guess.update()
            time.sleep(1)

        db.session.commit()

    app.logger.info("Finished updating manga chapter guesses")
