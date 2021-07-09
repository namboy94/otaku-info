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
from jerrycan.base import db
from jerrycan.db.User import User
from sqlalchemy.exc import IntegrityError
from otaku_info.db.MediaItem import MediaItem
from otaku_info.db.MediaIdMapping import MediaIdMapping
from otaku_info.db.MediaUserState import MediaUserState
from otaku_info.enums import ListService, MediaType, MediaSubType, \
    ReleasingState, ConsumingState
from otaku_info.test.TestFramework import _TestFramework


class TestMediaUserState(_TestFramework):
    """
    Class that tests the MediaUserState database model
    """

    def generate_sample_media_user_state(self) \
            -> Tuple[MediaUserState, User, MediaItem, MediaIdMapping]:
        """
        Generates a media user state
        :return: The media user state, user, media item and media id
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
        media_id = MediaIdMapping(
            media_item=media_item,
            service_id="101177",
            service=ListService.ANILIST,
            media_type=media_item.media_type,
            media_subtype=media_item.media_subtype
        )
        media_user_state = MediaUserState(
            media_id=media_id,
            user=user,
            progress=10,
            score=75,
            consuming_state=ConsumingState.CURRENT
        )
        db.session.add(media_item)
        db.session.add(media_id)
        db.session.add(media_user_state)
        db.session.commit()
        return media_user_state, user, media_item, media_id

    def test_json_representation(self):
        """
        Tests the JSON representation of the model
        :return: None
        """
        media_user_state, user, media_item, media_id = \
            self.generate_sample_media_user_state()

        self.assertEqual(
            media_user_state.__json__(False),
            {
                "id": media_id.id,
                "media_id_id": media_id.id,
                "user_id": user.id,
                "progress": media_user_state.progress,
                "volume_progress": None,
                "score": media_user_state.score,
                "consuming_state": media_user_state.consuming_state.name
            }
        )
        self.assertEqual(
            media_user_state.__json__(True),
            {
                "id": media_id.id,
                "media_id": media_id.__json__(True, ["media_user_states"]),
                "media_id_id": media_id.id,
                "user_id": user.id,
                "user": user.__json__(True, ["media_user_states"]),
                "progress": media_user_state.progress,
                "volume_progress": None,
                "score": media_user_state.score,
                "consuming_state": media_user_state.consuming_state.name,
                "media_notification": None,
                "media_list_items": []
            }
        )

    def test_string_representation(self):
        """
        Tests the string representation of the model
        :return: None
        """
        media_user_state, user, media_item, media_id = \
            self.generate_sample_media_user_state()
        data = media_user_state.__json__()
        data.pop("id")
        self.assertEqual(
            str(media_user_state),
            "MediaUserState:{} <{}>".format(media_user_state.id, data)
        )

    def test_repr(self):
        """
        Tests the __repr__ method of the model class
        :return: None
        """
        media_user_state, user, media_item, media_id = \
            self.generate_sample_media_user_state()
        generated = {"value": media_user_state}
        code = repr(media_user_state)

        exec("generated['value'] = " + code)
        self.assertEqual(generated["value"], media_user_state)
        self.assertFalse(generated["value"] is media_user_state)

    def test_hashing(self):
        """
        Tests using the model objects as keys in a dictionary
        :return: None
        """
        media_user_state, user, media_item, media_id = \
            self.generate_sample_media_user_state()
        media_user_state_2 = MediaUserState(
            media_id=media_id,
            user=self.generate_sample_user()[0],
            progress=15,
            score=85,
            consuming_state=ConsumingState.CURRENT
        )
        db.session.add(media_user_state_2)
        db.session.commit()
        mapping = {
            media_user_state: 100,
            media_user_state_2: 200
        }
        self.assertEqual(mapping[media_user_state], 100)
        self.assertEqual(mapping[media_user_state_2], 200)

    def test_equality(self):
        """
        Tests checking equality for model objects
        :return: None
        """
        media_user_state, user, media_item, media_id = \
            self.generate_sample_media_user_state()
        media_user_state_2 = MediaUserState(
            media_id=media_id,
            user=self.generate_sample_user()[0],
            progress=15,
            score=85,
            consuming_state=ConsumingState.CURRENT
        )
        db.session.add(media_user_state_2)
        db.session.commit()
        self.assertEqual(media_user_state, media_user_state)
        self.assertNotEqual(media_user_state, media_user_state_2)
        self.assertNotEqual(media_user_state, 100)

    def test_uniqueness(self):
        """
        Tests if the uniqueness of the model is handled properly
        :return: None
        """
        media_user_state, user, media_item, media_id = \
            self.generate_sample_media_user_state()

        standard_kwargs = media_user_state.__json__(False)
        standard_kwargs.pop("id")
        standard_kwargs["consuming_state"] = media_user_state.consuming_state

        media_id_kwargs = media_id.__json__(False)
        media_id_kwargs.pop("id")
        media_id_kwargs["service"] = ListService.KITSU
        media_id_kwargs["media_type"] = media_id.media_type
        media_id_kwargs["media_subtype"] = media_id.media_subtype
        new_media_id = MediaIdMapping(**media_id_kwargs)
        db.session.add(new_media_id)
        db.session.commit()

        try:
            duplicate = MediaUserState(**standard_kwargs)
            db.session.add(duplicate)
            db.session.commit()
            self.fail()
        except IntegrityError:
            db.session.rollback()

        for key, value, error_expected in [
            ("media_id_id", new_media_id.id, False),
            ("user_id", self.generate_sample_user(True)[0].id, False),
            ("progress", 1, True),
            ("score", 12, True),
            ("consuming_state", ConsumingState.PAUSED, True)
        ]:
            kwargs = dict(standard_kwargs)
            kwargs[key] = value
            try:
                generated = MediaUserState(**kwargs)
                db.session.add(generated)
                db.session.commit()
                if error_expected:
                    self.fail()
            except IntegrityError as e:
                db.session.rollback()
                if not error_expected:
                    raise e
