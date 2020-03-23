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


from typing import Dict, Any
from otaku_info_web.flask import db
from otaku_info_web.db.ModelMixin import ModelMixin


class ExternalUsername(ModelMixin, db.Model):
    """
    Model that describes the 'external_usernames' SQL table
    that stores the usernames of users on external sites like
    anilist.co
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the Model
        :param args: The constructor arguments
        :param kwargs: The constructor keyword arguments
        """
        super().__init__(*args, **kwargs)

    __tablename__ = "external_usernames"
    """
    The name of the table
    """

    user_id = db.Column(
        db.Integer, db.ForeignKey(
            "users.id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False
    )
    """
    The ID of the user associated with these external usernames
    """

    user = db.relationship(
        "User",
        backref=db.backref(
            "external_usernames", lazy=True, cascade="all,delete"
        )
    )
    """
    The user associated with these external usernames
    """

    anilist = db.Column(db.String(255))
    """
    Username for anilist.co
    """

    myanimelist = db.Column(db.String(255))
    """
    Username for myanimelist.net
    """

    kitsu = db.Column(db.String(255))
    """
    Username for kitsu.io
    """

    bakaupdates = db.Column(db.String(255))
    """
    Username for mangaupdates.com
    """

    mangadex = db.Column(db.String(255))
    """
    Username for mangadex.org
    """

    vndb = db.Column(db.String(255))
    """
    Username for vndb.org
    """

    anidb = db.Column(db.String(255))
    """
    Username for anidb.net
    """

    animeplanet = db.Column(db.String(255))
    """
    Username for anime-planet.com
    """

    lndb = db.Column(db.String(255))
    """
    Username for lndb.info
    """

    novelupdates = db.Column(db.String(255))
    """
    Username for novelupdates.com
    """

    @property
    def external_usernames(self) -> Dict[str, str]:
        """
        :return: A dictionary mapping site names to external usernames
        """
        base = self.__json__(False)
        base.pop("id")
        base.pop("user_id")
        return base

    @external_usernames.setter
    def external_usernames(self, _external: Dict[str, str]):
        """
        Sets the external usernames
        :param _external: A dictionary mapping site names to external usernames
        :return: None
        """
        external = {x: y if y != "" else None for x, y in _external.items()}
        self.anilist = external.get("anilist")
        self.myanimelist = external.get("myanimelist")
        self.kitsu = external.get("kitsu")
        self.anidb = external.get("anidb")
        self.bakaupdates = external.get("bakaupdates")
        self.mangadex = external.get("mangadex")
        self.lndb = external.get("lndb")
        self.novelupdates = external.get("novelupdates")
        self.animeplanet = external.get("animeplanet")
        self.vndb = external.get("vndb")

    def __json__(self, include_children: bool = False) -> Dict[str, Any]:
        """
        Generates a dictionary containing the information of this model
        :param include_children: Specifies if children data models will be
                                 included or if they're limited to IDs
        :return: A dictionary representing the model's values
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "anilist": self.anilist,
            "myanimelist": self.myanimelist,
            "kitsu": self.kitsu,
            "bakaupdates": self.bakaupdates,
            "mangadex": self.mangadex,
            "vndb": self.vndb,
            "anidb": self.anidb,
            "animeplanet": self.animeplanet,
            "lndb": self.lndb,
            "novelupdates": self.novelupdates
        }
        if include_children:
            data["user"] = self.user.__json__(include_children)
        return data
