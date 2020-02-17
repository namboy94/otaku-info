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

from typing import Dict, Tuple, Callable
from otaku_info_web.flask import db, app
from otaku_info_web.db.ExternalUsername import ExternalUsername
from otaku_info_web.enums import MediaType
from otaku_info_web.data.anilist import load_anilist
from otaku_info_web.db.AnilistEntry import AnilistEntry
from otaku_info_web.db.AnilistUserEntry import AnilistUserEntry


def update_anilist_entries():
    """
    Updates anilist entries
    :return: None
    """
    app.logger.info("Updating Anilist Entries")
    for external_username in ExternalUsername.query.all():
        anilist_user = external_username.anilist
        if anilist_user is None:
            continue

        for media_type in MediaType:

            anilist = load_anilist(anilist_user, media_type)
            for entry in anilist:

                media = entry["media"]
                anilist_id = media["id"]
                anilist_entry = AnilistEntry.query.filter_by(
                    anilist_id=anilist_id,
                    media_type=media_type
                ).first()

                if anilist_entry is None:
                    anilist_entry = AnilistEntry.from_data(media, media_type)
                    db.session.add(anilist_entry)
                else:
                    anilist_entry.update(media, media_type)

                db.session.commit()

                user_entry = AnilistUserEntry.query.filter_by(
                    user=external_username.user,
                    entry=anilist_entry
                ).first()

                if user_entry is None:
                    user_entry = AnilistUserEntry(
                        user=external_username.user,
                        entry=anilist_entry,
                        progress=entry["progress"],
                        score=entry["score"]
                    )
                    db.session.add(user_entry)
                else:
                    user_entry.progress = entry["progress"]
                    user_entry.score = entry["score"]

                db.session.commit()


def update_chapter_guesses():
    """
    Updates chapter guesses
    :return: None
    """
    app.logger.info("Updating Anilist Chapter Guesses")
    for anilist_entry in AnilistEntry.query.all():
        anilist_entry.update_chapter_guess()
        db.session.commit()
        app.logger.debug("Updated chapter guess for " + anilist_entry.name)


bg_tasks: Dict[str, Tuple[int, Callable]] = {
    # "anilist_entries_update": (5, update_anilist_entries),
    "anilist_chapter_guess_update": (5, update_chapter_guesses)
}
"""
A dictionary containing background tasks for the flask application
"""
