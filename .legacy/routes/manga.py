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

from typing import Union
from flask import render_template, Blueprint
from flask_login import login_required
from werkzeug import Response
from otaku_info_web.db.MediaItem import AnilistEntry
from otaku_info_web.db.AnilistUserEntry import AnilistUserEntry
from otaku_info_web.db.AnilistCustomList import AnilistCustomList
from otaku_info_web.db.AnilistCustomListItem import AnilistCustomListItem

manga_blueprint = Blueprint("manga", __name__)


@manga_blueprint.route("/manga", methods=["GET"])
@login_required
def manga() -> Union[Response, str]:

    ubooquity_list = \
        AnilistCustomList.query.filter_by(name="Ubooquity").first()
    ubooquity_items = \
        AnilistCustomListItem.query.filter_by(custom_list=ubooquity_list)
    entries = [x.user_entry for x in ubooquity_items]

    return render_template("proto/manga.html", entries=entries)
