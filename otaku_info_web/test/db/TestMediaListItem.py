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

from typing import Tuple
from puffotter.flask.base import db
from puffotter.flask.db.User import User
from sqlalchemy.exc import IntegrityError
from otaku_info_web.db.MediaItem import MediaItem
from otaku_info_web.db.MediaId import MediaId
from otaku_info_web.db.MediaUserState import MediaUserState
from otaku_info_web.db.MediaList import MediaList
from otaku_info_web.db.MediaListItem import MediaListItem
from otaku_info_web.utils.enums import ListService, MediaType, MediaSubType, \
    ReleasingState, ConsumingState
from otaku_info_web.test.TestFramework import _TestFramework


class TestMediaListItem(_TestFramework):
    """
    Class that tests the MediaListItem database model
    """

    def generate_sample_media_list_item(self) -> Tuple[
        MediaListItem, MediaList, MediaUserState, User, MediaItem, MediaId
    ]:
        """
        Generates a media list item
        :return: The media list item, media list, media user state, user,
                 media item and media id
        """
        user = self.generate_sample_user(True)[0]
        media_item = MediaItem(
            media_type=MediaType.MANGA,
            media_subtype=MediaSubType.MANGA,
            english_title="Fly Me to the Moon",
            romaji_title="Tonikaku Cawaii",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/manga/"
                      "cover/medium/nx101177-FjjD5UWB3C3t.png",
            latest_release=None,
            releasing_state=ReleasingState.RELEASING
        )
        media_id = MediaId(
            media_item=media_item,
            service_id="101177",
            service=ListService.ANILIST
        )
        media_user_state = MediaUserState(
            media_id=media_id,
            user=user,
            progress=10,
            score=75,
            consuming_state=ConsumingState.CURRENT
        )
        media_list = MediaList(
            name="ABC",
            user=user,
            service=ListService.ANILIST,
            media_type=MediaType.MANGA
        )
        media_list_item = MediaListItem(
            media_list=media_list,
            media_user_state=media_user_state
        )
        db.session.add(media_item)
        db.session.add(media_id)
        db.session.add(media_user_state)
        db.session.add(media_list)
        db.session.add(media_list_item)
        db.session.commit()
        return media_list_item, media_list, media_user_state, \
            user, media_item, media_id

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        media_list_item, media_list, media_user_state, \
            user, media_item, media_id = \
            self.generate_sample_media_list_item()

        self.assertEqual(
            media_list_item.__json__(False),
            {
                "id": media_id.id,
                "media_list_id": media_list.id,
                "media_user_state_id": media_user_state.id
            }
        )
        self.assertEqual(
            media_list_item.__json__(True),
            {
                "id": media_id.id,
                "media_list_id": media_list.id,
                "media_list": media_list.__json__(True),
                "media_user_state_id": media_user_state.id,
                "media_user_state": media_user_state.__json__(True)
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        media_list_item, media_list, media_user_state, \
            user, media_item, media_id = \
            self.generate_sample_media_list_item()
        data = media_list_item.__json__()
        data.pop("id")
        self.assertEqual(
            str(media_list_item),
            "MediaListItem:{} <{}>".format(media_list_item.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        media_list_item, media_list, media_user_state, \
            user, media_item, media_id = \
            self.generate_sample_media_list_item()
        generated = {"value": media_list_item}
        code = repr(media_list_item)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], media_list_item)
        self.assertFalse(generated["value"] is media_list_item)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        media_list_item, media_list, media_user_state, \
            user, media_item, media_id = \
            self.generate_sample_media_list_item()
        media_list_2 = MediaList(
            name="XYZ",
            user=user,
            service=ListService.ANILIST,
            media_type=MediaType.MANGA
        )
        media_list_item_2 = MediaListItem(
            media_list=media_list_2,
            media_user_state=media_user_state
        )
        db.session.add(media_list_2)
        db.session.add(media_list_item_2)
        db.session.commit()
        mapping = {
            media_list_item: 100,
            media_list_item_2: 200
        }
        self.assertEqual(mapping[media_list_item], 100)
        self.assertEqual(mapping[media_list_item_2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        media_list_item, media_list, media_user_state, \
            user, media_item, media_id = \
            self.generate_sample_media_list_item()
        media_list_2 = MediaList(
            name="XYZ",
            user=user,
            service=ListService.ANILIST,
            media_type=MediaType.MANGA
        )
        media_list_item_2 = MediaListItem(
            media_list=media_list_2,
            media_user_state=media_user_state
        )
        db.session.add(media_list_2)
        db.session.add(media_list_item_2)
        db.session.commit()
        self.assertEqual(media_list_item, media_list_item)
        self.assertNotEqual(media_list_item, media_list_item_2)
        self.assertNotEqual(media_list_item, 100)

    def test_uniqueness(self):
        """
        Tests if the uniqueness of the model is handled properly
        :return: None
        """
        media_list_item, media_list, media_user_state, \
            user, media_item, media_id = \
            self.generate_sample_media_list_item()

        standard_kwargs = media_list_item.__json__(False)
        standard_kwargs.pop("id")

        media_list_kwargs = media_list.__json__(False)
        media_list_kwargs.pop("id")
        media_list_kwargs["service"] = ListService.KITSU
        media_list_kwargs["media_type"] = MediaType.ANIME
        new_media_list = MediaList(**media_list_kwargs)
        db.session.add(new_media_list)
        db.session.commit()

        media_user_state_kwargs = media_user_state.__json__(False)
        media_user_state_kwargs.pop("id")
        media_user_state_kwargs["user_id"] = \
            self.generate_sample_user(True)[0].id
        media_user_state_kwargs["consuming_state"] \
            = media_user_state.consuming_state
        new_media_user_state = MediaUserState(**media_user_state_kwargs)
        db.session.add(new_media_user_state)
        db.session.commit()

        try:
            duplicate = MediaListItem(**standard_kwargs)
            db.session.add(duplicate)
            db.session.commit()
            self.fail()
        except IntegrityError:
            db.session.rollback()

        for key, value in [
            ("media_list_id", new_media_list.id),
            ("media_user_state_id", new_media_user_state.id)
        ]:
            kwargs = dict(standard_kwargs)
            kwargs[key] = value

            generated = MediaListItem(**kwargs)
            db.session.add(generated)
            db.session.commit()
