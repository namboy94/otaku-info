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

from datetime import datetime
from flask import request, render_template, redirect, url_for
from flask.blueprints import Blueprint
from flask_login import login_required, current_user
from puffotter.flask.base import db
from otaku_info.db.LnRelease import LnRelease
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.db.MediaId import MediaId
from otaku_info.enums import MediaSubType, ConsumingState
from otaku_info.utils.dates import MONTHS, map_month_name_to_month_number, \
    map_month_number_to_month_name
from otaku_info.utils.manga_updates.MangaUpdate import RelatedMangaId as \
    RelatedId


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/ln/releases", methods=["GET"])
    def ln_releases():
        """
        Displays light novel releases
        :return: The response
        """
        try:
            year = int(request.args.get("year"))
        except (TypeError, ValueError):
            year = None
        try:
            month = int(request.args["month"])
        except KeyError:
            month = None
        except (TypeError, ValueError):
            month_string = request.args["month"]
            if month_string.lower() == "all":
                month = None
            else:
                month = map_month_name_to_month_number(month_string)

        now = datetime.utcnow()
        if not (year is not None and month is None):
            if year is None:
                year = now.year
            if month is None:
                month = now.month

        all_releases = LnRelease.query.all()
        years = list(set([x.release_date.year for x in all_releases]))
        years.sort()

        releases = [
            x for x in all_releases
            if x.release_date.year == year
        ]
        if month is not None:
            releases = [x for x in releases if x.release_date.month == month]
        releases.sort(key=lambda x: x.release_date)

        if month is None:
            month_name = "all"
        else:
            month_name = map_month_number_to_month_name(month)

        return render_template(
            "ln/ln_releases.html",
            releases=releases,
            years=years,
            months=MONTHS + ["all"],
            selected_year=year,
            selected_month=month_name
        )

    @blueprint.route("/ln/releases", methods=["POST"])
    def ln_releases_form():
        """
        Handles form requests and forwards it to the appropriate GET URL.
        """
        year = request.form.get("year")
        month = request.form.get("month")
        get_url = url_for("ln.ln_releases") + f"?year={year}&month={month}"
        return redirect(get_url)

    @blueprint.route("/ln/updates", methods=["GET"])
    @login_required
    def ln_updates():

        today = datetime.utcnow().strftime("%Y-%m-%d")

        media_user_states = [
            x for x in
            MediaUserState.query
            .filter_by(user=current_user)
            .filter_by(consuming_state=ConsumingState.CURRENT)
            .options(
                db.joinedload(MediaUserState.media_id)
                  .subqueryload(MediaId.media_item)
            )
            .all()
            if x.media_id.media_item.media_subtype == MediaSubType.NOVEL
        ]
        all_ln_releases = LnRelease.query\
            .filter(LnRelease.release_date_string <= today)\
            .all()
        media_item_ids = [x.media_id.media_item.id for x in media_user_states]
        media_ids = MediaId.query\
            .filter(MediaId.media_item_id.in_(media_item_ids))\
            .all()

        related_ids = {}
        for media_id in media_ids:
            if media_id.media_item_id not in related_ids:
                related_ids[media_id.media_item_id] = []
            related = RelatedId(media_id.service, media_id.service_id)
            related_ids[media_id.media_item_id].append(related)

        newest_ln_releases = {}
        for ln_release in all_ln_releases:
            media_item_id = ln_release.media_item_id
            existing = newest_ln_releases.get(media_item_id)

            if existing is None \
                    or existing.release_date < ln_release.release_date:
                newest_ln_releases[media_item_id] = ln_release

        media_user_states.sort(key=lambda x: x.score, reverse=True)

        return render_template(
            "ln/ln_updates.html",
            ln_releases=newest_ln_releases,
            user_states=media_user_states,
            related_ids=related_ids
        )

    return blueprint
