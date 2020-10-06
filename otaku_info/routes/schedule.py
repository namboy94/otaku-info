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
from flask import render_template
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from jerrycan.base import db
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.MediaId import MediaId


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines a Blueprint that handles schedule-related stuff
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/seasonal_schedule")
    @login_required
    def seasonal_schedule():
        """
        Shows the seasonal anime schedule for a user's media entries
        :return: None
        """
        media_user_states: List[MediaUserState] = MediaUserState.query\
            .options(
                db.joinedload(MediaUserState.media_id)
                .subqueryload(MediaId.media_item)
            )\
            .filter_by(user_id=current_user.id)\
            .all()
        media_user_states = [
            x for x in media_user_states
            if x.media_id.media_item.next_episode_airing_time is not None
        ]

        weekdays = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday"
        }
        entries_by_weekday = []

        for weekday, weekday_name in weekdays.items():
            entries = []
            for user_state in media_user_states:
                next_airing = \
                    user_state.media_id.media_item.next_episode_datetime
                if next_airing.isoweekday() == weekday:
                    entries.append(user_state)
            entries.sort(
                key=lambda x: x.media_id.media_item.next_episode_airing_time
            )
            entries_by_weekday.append((weekday_name, entries))

        return render_template(
            "schedule/seasonal_schedule.html",
            schedule=entries_by_weekday
        )

    return blueprint
