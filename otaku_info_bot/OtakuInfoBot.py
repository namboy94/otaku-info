"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-bot.

otaku-info-bot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-bot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-bot.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from kudubot.Bot import Bot
from kudubot.db.Address import Address
from kudubot.parsing.CommandParser import CommandParser
from sqlalchemy.orm import Session
from otaku_info_bot.OtakuInfoCommandParser import OtakuInfoCommandParser
from otaku_info_bot.fetching.anime import load_newest_episodes
from otaku_info_bot.fetching.ln import load_ln_releases
from otaku_info_bot.db.AnilistEntry import AnilistEntry
from otaku_info_bot.db.Notification import Notification
from otaku_info_bot.db.config import NotificationConfig, \
    MangaNotificationConfig, AnimeNotificationConfig
from otaku_info_bot.fetching.anilist import guess_latest_manga_chapter, \
    load_anilist


class OtakuInfoBot(Bot):
    """
    The OtakuInfo Bot class that defines the anime reminder
    functionality.
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the bot
        """
        return "otaku-info-bot"

    @classmethod
    def parsers(cls) -> List[CommandParser]:
        """
        :return: A list of parser the bot supports for commands
        """
        return [OtakuInfoCommandParser()]

    def activate_config(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session,
            config_cls: type(NotificationConfig)
    ):
        """
        Activates a configuration for a user
        :param address: The user's address
        :param args: The command arguments
        :param db_session: The database session
        :param config_cls: The configuration class
        :return: None
        """
        exists = db_session.query(config_cls)\
            .filter_by(address=address).first() is not None

        if exists:
            msg = "Configuration already activated"
            self.send_txt(address, msg, "Already Active")

        else:
            username = args["anilist-username"]
            default_list_name = config_cls.default_list_name()
            config = config_cls(
                anilist_username=username,
                address=address,
                list_name=args.get("custom-list", default_list_name)
            )
            db_session.add(config)
            db_session.commit()

            self.send_txt(address, "Configuration Activated", "Activated")

    def deactivate_config(
            self,
            address: Address,
            db_session: Session,
            config_cls: type(NotificationConfig)
    ):
        """
        Deactivates an anilist configuration for a user
        :param address: The address for which to deactivate the config
        :param db_session: The database session to use
        :param config_cls: The configuration class to use
        :return: None
        """
        existing = db_session.query(config_cls) \
            .filter_by(address=address).first()

        if existing is not None:
            db_session.delete(existing)

            for notification in db_session.query(Notification)\
                    .filter_by(address=address).all():
                if notification.entry.media_type == config_cls.media_type():
                    db_session.delete(notification)

            db_session.commit()

        self.send_txt(address, "Deactivated Configuration", "Deactivated")

    def _update_anilist_entries(self, db_session: Session):
        """
        Updates anilist entries in the database
        :param db_session: The database session to use
        :return: None
        """
        self.logger.info("Updating anilist entries")

        newest_anime_episodes = load_newest_episodes()
        manga_progress = {}

        for config_cls in [AnimeNotificationConfig, MangaNotificationConfig]:

            media_type = config_cls.media_type()

            for config in db_session.query(config_cls).all():
                anilist = load_anilist(
                    config.anilist_username,
                    media_type,
                    config.list_name
                )

                anilist_ids = []
                for entry in anilist:

                    anilist_id = entry["media"]["id"]
                    anilist_ids.append(anilist_id)

                    romaji_name = entry["media"]["title"]["romaji"]
                    english_name = entry["media"]["title"]["english"]
                    name = romaji_name
                    if media_type == "manga" and english_name is not None:
                        name = english_name

                    user_progress = entry["progress"]

                    if media_type == "anime":
                        latest = newest_anime_episodes.get(anilist_id)
                        if latest is None:
                            next_ep = entry["media"]["nextAiringEpisode"]
                            if next_ep is not None:
                                latest = next_ep["episode"] - 1
                        if latest is None:
                            latest = entry["media"]["episodes"]
                    else:  # media_type == "manga":
                        latest = entry["media"]["chapters"]
                        if latest is None:
                            latest = manga_progress.get(anilist_id)
                        if latest is None:
                            latest = guess_latest_manga_chapter(anilist_id)
                        manga_progress[anilist_id] = latest

                    db_entry = db_session.query(AnilistEntry).filter_by(
                        anilist_id=anilist_id, media_type=media_type
                    ).first()
                    if db_entry is None:
                        db_entry = AnilistEntry(
                            anilist_id=anilist_id,
                            name=name,
                            latest=latest,
                            media_type=media_type
                        )
                        db_session.add(db_entry)
                    elif latest != 0:
                        db_entry.latest = latest

                    notification = db_session.query(Notification).filter_by(
                        entry=db_entry, address=config.address
                    ).first()

                    if notification is None:
                        notification = Notification(
                            address=config.address,
                            entry=db_entry,
                            user_progress=user_progress,
                            last_update=user_progress
                        )
                        db_session.add(notification)
                    else:
                        notification.user_progress = user_progress

                # Purge stale entries
                for existing in db_session.query(Notification) \
                        .filter_by(address=config.address).all():
                    if existing.entry.media_type != media_type:
                        continue
                    elif existing.entry.anilist_id not in anilist_ids:
                        db_session.delete(existing)

        db_session.commit()
        self.logger.info("Finished updating anilist entries")

    def _send_notifications(
            self,
            db_session: Session,
            address_limit: Optional[Address] = None,
            use_user_progress: bool = False,
            media_type_limit: Optional[str] = None
    ):
        """
        Sends out any due notifications
        :param db_session: The database session to use
        :param address_limit: Can be set to limit this to a single user
        :param use_user_progress: Instead of looking at the last time a
                                  notification was sent out, look at the user's
                                  progress
        :param media_type_limit: Limits the media type of the notifications to
                                 be sent
        :return: None
        """
        self.logger.info("Sending Notifications")

        due = {}

        for notification in db_session.query(Notification).all():

            address_id = notification.address_id
            if address_limit is not None and address_limit.id != address_id:
                continue

            if address_id not in due:
                due[address_id] = {
                    "address": notification.address,
                    "anime": [],
                    "manga": []
                }

            media_type = notification.entry.media_type
            if notification.diff > 0:
                due[address_id][media_type].append(notification)
            elif use_user_progress and notification.user_diff > 0:
                due[address_id][media_type].append(notification)

        for _, data in due.items():
            address = data["address"]

            for media_type in ["manga", "anime"]:

                if media_type_limit is not None \
                        and media_type != media_type_limit:
                    continue

                notifications = data[media_type]
                notifications.sort(key=lambda x: x.user_diff, reverse=True)

                media_name = media_type[0].upper() + media_type[1:]
                unit_type = "Episode" if media_type == "anime" else "Chapter"

                if len(notifications) <= 5:
                    for notification in notifications:
                        message = "{} {} {} was released\n\n"
                        message += "Current Progress: {}/{} (+{})\n\n{}"
                        message = message.format(
                            notification.entry.name,
                            unit_type,
                            notification.entry.latest,
                            notification.user_progress,
                            notification.entry.latest,
                            notification.user_diff,
                            notification.entry.anilist_url
                        )
                        self.send_txt(address, message, "Notification")
                else:
                    message = "New {} {}s:\n\n".format(media_name, unit_type)
                    for notification in notifications:
                        message += "\\[+{}] {} {} {}\n".format(
                            notification.user_diff,
                            notification.entry.name,
                            unit_type,
                            notification.entry.latest
                        )
                    self.send_txt(address, message, "Notifications")

                for notification in notifications:
                    notification.last_update = notification.entry.latest

        db_session.commit()
        self.logger.info("Finished Sending Notifications")

    def _on_activate_anime_notifications(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Activates anime notifications for a user
        :param address: The user's address
        :param args: The arguments, containing the anilist username
        :param db_session: The database session to use
        :return: None
        """
        self.activate_config(
            address, args, db_session, AnimeNotificationConfig
        )

    def _on_deactivate_anime_notifications(
            self,
            address: Address,
            _,
            db_session: Session
    ):
        """
        Deactivates anime notifications for a user
        :param address: The user's address
        :param db_session: The database session to use
        :return: None
        """
        self.deactivate_config(address, db_session, AnimeNotificationConfig)

    def on_list_new_anime_episodes(
            self,
            address: Address,
            _,
            db_session: Session
    ):
        """
        Handles listing new episodes for a user
        :param address: The address that requested this
        :param _: The arguments
        :param db_session: The database session to use
        :return: None
        """
        self._send_notifications(db_session, address, True, "anime")

    def _on_activate_manga_notifications(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles activating manga notifications for a user using anilist
        :param address: The user that sent this request
        :param args: The arguments to use
        :param db_session: The database session to use
        :return: None
        """
        self.activate_config(
            address, args, db_session, MangaNotificationConfig
        )

    def _on_deactivate_manga_notifications(
            self,
            address: Address,
            _,
            db_session: Session
    ):
        """
        Handles deactivating manga notifications for a user using anilist
        :param address: The user that sent this request
        :param db_session: The database session to use
        :return: None
        """
        self.deactivate_config(address, db_session, MangaNotificationConfig)

    def on_list_new_manga_chapters(
            self,
            address: Address,
            _,
            db_session: Session
    ):
        """
        Handles listing new manga chapters for a user
        :param address: The address that requested this
        :param _: The arguments
        :param db_session: The database session to use
        :return: None
        """
        self._send_notifications(db_session, address, True, "manga")

    def _on_list_ln_releases(
            self,
            address: Address,
            args: Dict[str, Any],
            _
    ):
        """
        Handles listing current light novel releases
        :param address: The user that sent this request
        :param args: The arguments to use
        :return: None
        """
        year = args.get("year")
        month = args.get("month")

        now = datetime.utcnow()

        if year is None:
            year = now.year
        if month is None:
            month = now.strftime("%B")

        releases = load_ln_releases().get(year, {}).get(month.lower(), [])
        body = "Light Novel Releases {} {}\n\n".format(month, year)

        for entry in releases:
            body += "{}: {} {}\n".format(
                entry["day"],
                entry["title"],
                entry["volume"]
            )
        self.send_txt(address, body)

    def bg_iteration(self, _: int, db_session: Session):
        """
        Periodically checks for new notifications and sends them out
        :param _: The iteration count
        :param db_session: The database session to use
        :return: None
        """
        self._update_anilist_entries(db_session)
        self._send_notifications(db_session)
