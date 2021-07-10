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

# imports
import os
import sys
from subprocess import Popen, check_output
from setuptools import setup, find_packages


if __name__ == "__main__":

    if sys.argv[1] == "install":
        # Static dependencies (JS and CSS)
        Popen([
            "npm", "install", "--prefix", "otaku_info/static"
        ]).wait()
        Popen(["sass", "--update", "--force", "--style", "compressed",
               "otaku_info/static/scss/style.scss",
               "otaku_info/static/scss"]).wait()
        js_dir = "otaku_info/static/javascript"
        minified = b""
        for js_file in os.listdir(js_dir):
            if js_file == "min.js":
                continue
            js_path = os.path.join(js_dir, js_file)
            minified += check_output(["yui-compressor", js_path]) + b"\n"
        with open(os.path.join(js_dir, "min.js"), "wb") as f:
            f.write(minified)

    setup(
        name="otaku-info",
        version=open("version", "r").read(),
        description="Website providing information on Japanese entertainment "
                    "media",
        long_description=open("README.md", "r").read(),
        long_description_content_type="text/markdown",
        classifiers=[
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
        ],
        url="https://gitlab.namibsun.net/namibsun/python/otaku-info",
        author="Hermann Krumrey",
        author_email="hermann@krumreyh.com",
        license="GNU GPL3",
        packages=find_packages(),
        scripts=list(map(lambda x: os.path.join("bin", x), os.listdir("bin"))),
        install_requires=[
            "Flask",
            "werkzeug",
            "flask_sqlalchemy",
            "flask_login",
            "puffotter[crypto]",
            "requests",
            "sqlalchemy==1.3.19",
            "bokkichat",
            "beautifulsoup4",
            "jerrycan"
        ],
        include_package_data=True,
        zip_safe=False
    )
