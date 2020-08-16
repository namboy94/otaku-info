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

# noinspection PyProtectedMember
from puffotter.flask.test.TestFramework import \
    _TestFramework as __TestFrameWork
from otaku_info_web.main import root_path
from otaku_info_web.Config import Config
from otaku_info_web.routes import blueprint_generators
from otaku_info_web.db import models


class _TestFramework(__TestFrameWork):
    """
    Class that models a testing framework for the flask application
    """
    module_name = "otaku_info_web"
    root_path = root_path
    config = Config
    models = models
    blueprint_generators = blueprint_generators
