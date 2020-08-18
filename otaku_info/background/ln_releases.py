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

from puffotter.flask.base import app
from otaku_info.utils.ln.ln_releases import load_ln_releases


def update_ln_releases():
    """
    Updates the light novel releases
    :return: None
    """
    app.logger.info("Starting Light Novel Release Update")
    year = 2017
    releases = [1]
    while len(releases) > 0:
        year += 1
        app.logger.debug(f"Light Novel Release Update: {year}")
        releases = load_ln_releases(year)
    app.logger.info("Finished Light Novel Release Update")
