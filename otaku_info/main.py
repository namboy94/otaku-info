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

from puffotter.env import load_env_file
from jerrycan.initialize import init_flask
from jerrycan.wsgi import start_server
from otaku_info import sentry_dsn, root_path
from otaku_info.background import bg_tasks
from otaku_info.Config import Config
from otaku_info.routes import blueprint_generators
from otaku_info.db import models


def main():
    """
    Starts the flask application
    :return: None
    """
    load_env_file()
    init_flask(
        "otaku_info",
        sentry_dsn,
        root_path,
        Config,
        models,
        blueprint_generators
    )
    start_server(Config, bg_tasks)
