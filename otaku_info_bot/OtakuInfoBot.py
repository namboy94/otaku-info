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

import time
from typing import Dict, List, Any
from datetime import datetime
from kudubot.Bot import Bot
from kudubot.db.Address import Address
from kudubot.parsing.CommandParser import CommandParser
from sqlalchemy.orm import Session
from otaku_info_bot.OtakuInfoCommandParser import OtakuInfoCommandParser
from otaku_info_bot.fetching.anime import load_newest_episodes
from otaku_info_bot.fetching.ln import load_ln_releases
from otaku_info_bot.db.AnimeEntry import AnimeEntry
from otaku_info_bot.db.AnimeReminder import AnimeReminder
from otaku_info_bot.db.AnimeReminderConfig import AnimeReminderConfig
from otaku_info_bot.db.MangaEntry import MangaEntry
from otaku_info_bot.db.MangaUpdate import MangaUpdate
from otaku_info_bot.db.MangaUpdateConfig import MangaUpdateConfig
from otaku_info_bot.fetching.anilist import load_user_manga_list, \
    guess_latest_manga_chapter, load_user_anime_list


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

    @property
    def bg_pause(self) -> int:
        """
        :return: 30 seconds
        """
        return 30

    # Anime ------------------------------------------------------------------

    def _on_activate_anime_reminders(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Activates anime reminder for a user
        :param address: The user's address
        :param args: The arguments, containing the anilist username
        :param db_session: The database session to use
        :return: None
        """
        exists = db_session.query(AnimeReminderConfig)\
            .filter_by(address=address).first() is not None
        if exists:
            self.send_txt(
                address, "Anime Reminder already activated", "Already Active"
            )
            return

        username = args["anilist-username"]
        config = AnimeReminderConfig(
            anilist_username=username,
            address=address
        )
        db_session.add(config)
        db_session.commit()

        self.send_txt(address, "Anime Reminders Activated", "Activated")

    def _on_deactivate_anime_reminders(
            self,
            address: Address,
            _,
            db_session: Session
    ):
        """
        Deactivates anime reminders for a user
        :param address: The user's address
        :param db_session: The database session to use
        :return: None
        """
        existing = db_session.query(AnimeReminderConfig) \
            .filter_by(address=address).first()
        if existing is not None:
            db_session.delete(existing)

            for reminder in db_session.query(AnimeReminder) \
                    .filter_by(address=address).all():
                db_session.delete(reminder)

            db_session.commit()

        self.send_txt(address, "Deactivated Anime Reminders", "Deactivated")

    def _update_anime_entries(self, db_session: Session):
        """
        Updates anime entries
        :param db_session: The database session to use
        :return: None
        """
        self.logger.info("Updating anime entries")
        newest_episodes = load_newest_episodes()

        for config in db_session.query(AnimeReminderConfig).all():
            anilist = load_user_anime_list(config.anilist_username, "Watching")

            anilist_ids = []
            for entry in anilist:

                anilist_id = entry["media"]["id"]
                anilist_ids.append(anilist_id)

                name = entry["media"]["title"]["romaji"]
                user_episodes = entry["progress"]

                latest_episode = newest_episodes.get(anilist_id, 0)

                anime_entry = db_session.query(AnimeEntry) \
                    .filter_by(id=anilist_id).first()
                anime_reminder = db_session.query(AnimeReminder) \
                    .filter_by(entry_id=anilist_id, address=config.address) \
                    .first()

                if anime_entry is None:
                    anime_entry = AnimeEntry(
                        id=anilist_id,
                        name=name,
                        latest_episode=latest_episode
                    )
                    db_session.add(anime_entry)
                elif latest_episode != 0:
                    anime_entry.latest_episode = latest_episode

                if anime_reminder is None:
                    anime_reminder = AnimeReminder(
                        address=config.address,
                        entry=anime_entry,
                        last_update=user_episodes
                    )
                    db_session.add(anime_reminder)

            # Purge stale entries
            for existing in db_session.query(AnimeReminder) \
                    .filter_by(address=config.address).all():
                if existing.entry.id not in anilist_ids:
                    db_session.delete(existing)

        db_session.commit()
        self.logger.info("Finished updating anime entries")

    def _send_anime_reminders(self, db_session: Session):
        """
        Sends out any due anime reminders
        :param db_session: The database session
        :return: None
        """

        self.logger.info("Sending Anime Reminders")

        for config in db_session.query(AnimeReminderConfig).all():
            due = []
            for reminder in db_session.query(AnimeReminder)\
                    .filter_by(address=config.address).all():
                if reminder.diff > 0:
                    due.append(reminder)

            if len(due) <= 10:
                for reminder in due:
                    message = "\\[{}] {} Episode {}\n{}".format(
                        reminder.diff,
                        reminder.entry.name,
                        reminder.entry.latest_episode,
                        reminder.entry.anilist_url
                    )
                    self.send_txt(config.address, message, "Anime Reminders")
            else:
                message = "New Anime Episodes:\n\n"
                for reminder in due:
                    message += "\\[{}] {} Episode {}\n".format(
                        reminder.diff,
                        reminder.entry.name,
                        reminder.entry.latest_episode
                    )
                self.send_txt(config.address, message, "Anime Reminders")

            for reminder in due:
                reminder.last_update = reminder.entry.latest_episode

        db_session.commit()
        self.logger.info("Finished Sending Anime Reminders")

    # Light Novels -----------------------------------------------------------

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

    # Manga -----------------------------------------------------------------

    def _on_activate_manga_updates(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles activating manga updates for a user using anilist
        :param address: The user that sent this request
        :param args: The arguments to use
        :param db_session: The database session to use
        :return: None
        """
        exists = db_session.query(MangaUpdateConfig.id)\
            .filter_by(address=address).first() is not None
        if exists:
            self.send_txt(
                address, "Manga Updates already activated", "Already Active"
            )
            return

        username = args["anilist-username"]
        custom_list = args["custom-list"]
        config = MangaUpdateConfig(
            anilist_username=username,
            custom_list=custom_list,
            address=address
        )
        db_session.add(config)
        db_session.commit()

        self.send_txt(address, "Manga Updates Activated", "Activated")

    def _on_deactivate_manga_updates(
            self,
            address: Address,
            _,
            db_session: Session
    ):
        """
        Handles listing current light novel releases
        :param address: The user that sent this request
        :param db_session: The database session to use
        :return: None
        """
        existing = db_session.query(MangaUpdateConfig)\
            .filter_by(address=address).first()
        if existing is not None:
            db_session.delete(existing)

            for update in db_session.query(MangaUpdate)\
                    .filter_by(address=address).all():
                db_session.delete(update)

            db_session.commit()

        self.send_txt(address, "Deactivated Manga Updates", "Deactivated")

    def on_list_new_manga_chapters(
            self,
            address: Address,
            _,
            db_session: Session
    ):
        """
        Handles list_manga_updates command
        :param address: The address that requested this
        :param _: The arguments
        :param db_session: The database session to use
        :return: None
        """
        config = db_session.query(MangaUpdateConfig) \
            .filter_by(address=address).first()
        if config is None:
            self.send_txt(address, "No updates configured", "Not configured")
            return

        user_entries = load_user_manga_list(
            config.anilist_username, config.custom_list
        )
        progress = {}
        for entry in user_entries:
            anilist_id = entry["media"]["id"]
            chapter = entry["progress"]
            progress[anilist_id] = chapter

        updates = db_session.query(MangaUpdate)\
            .filter_by(address=address).all()

        for update in updates:
            update.last_update = progress[update.entry.id]

        self._send_manga_update_messages(address, updates)
        db_session.rollback()

    def _update_manga_entries(self, db_session: Session):
        """
        Updates the internal database of the manga entries with the newest
        information
        :param db_session: The database session to use
        :return: None
        """
        self.logger.info("Updating Manga Entries")
        configs = db_session.query(MangaUpdateConfig).all()

        manga_progress = {}

        for config in configs:  # type: MangaUpdateConfig
            anilist = load_user_manga_list(
                config.anilist_username, config.custom_list
            )

            anilist_ids = []

            for entry in anilist:

                anilist_id = entry["media"]["id"]
                anilist_ids.append(anilist_id)

                name = entry["media"]["title"]["english"]
                if name is None:
                    name = entry["media"]["title"]["romaji"]
                user_chapters = entry["progress"]

                chapters = entry["media"]["chapters"]
                if chapters is None:
                    chapters = manga_progress.get(anilist_id)
                if chapters is None:
                    chapters = guess_latest_manga_chapter(anilist_id)
                manga_progress[anilist_id] = chapters

                manga_entry = db_session.query(MangaEntry)\
                    .filter_by(id=anilist_id).first()
                manga_update = db_session.query(MangaUpdate)\
                    .filter_by(entry_id=anilist_id, address=config.address)\
                    .first()

                if manga_entry is None:
                    manga_entry = MangaEntry(
                        id=anilist_id,
                        name=name,
                        latest_chapter=chapters
                    )
                    db_session.add(manga_entry)
                else:
                    manga_entry.latest_chapter = chapters

                if manga_update is None:
                    manga_update = MangaUpdate(
                        address=config.address,
                        entry=manga_entry,
                        last_update=user_chapters
                    )
                    db_session.add(manga_update)

            # Purge stale entries
            for existing in db_session.query(MangaUpdate)\
                    .filter_by(address=config.address).all():
                if existing.entry.id not in anilist_ids:
                    db_session.delete(existing)

        db_session.commit()
        self.logger.info("Finished updating manga entries")

    def _send_manga_updates(self, db_session: Session):
        """
        Sends manga updates to the users with activated manga updates
        :return: None
        """
        self.logger.info("Sending Manga Updates")
        configs = db_session.query(MangaUpdateConfig).all()
        for config in configs:  # type: MangaUpdateConfig
            updates = db_session.query(MangaUpdate)\
                .filter_by(address=config.address).all()

            self._send_manga_update_messages(config.address, updates)

            for update in list(filter(lambda x: x.diff > 0, updates)):
                update.last_update = update.entry.latest_chapter

        db_session.commit()
        self.logger.info("Finished Sending Manga Updates")

    def _send_manga_update_messages(
            self,
            address: Address,
            updates: List[MangaUpdate],
            send_if_none_due: bool = False
    ):
        """
        Sends manga update messages.
        :param address: The address to send the message(s) to.
        :param updates: The updates to send
        :param send_if_none_due: If True, will always send a message
        :return: None
        """
        updates.sort(key=lambda x: x.diff, reverse=True)
        due = []
        for update in updates:  # type: MangaUpdate
            if update.diff > 0:
                due.append(update)

        if len(due) == 0:
            if send_if_none_due:
                self.send_txt(address, "No New Updates", "No New Updates")
            return

        if len(due) <= 10:
            for update in due:
                message = "\\[{}] {} Chapter {}\n{}".format(
                    update.diff,
                    update.entry.name,
                    update.entry.latest_chapter,
                    update.entry.anilist_url
                )
                self.send_txt(address, message, "Manga Updates")
        else:
            message = "New Manga Updates:\n\n"
            for update in due:
                message += "\\[{}] {} Chapter {}\n".format(
                    update.diff,
                    update.entry.name,
                    update.entry.latest_chapter
                )
            self.send_txt(address, message, "Manga Updates")

    def bg_iteration(self, _: int, db_session: Session):
        """
        Periodically checks for new reminders to update and manga updates
        :param _: The iteration count
        :param db_session: The database session to use
        :return:
        """
        self._update_anime_entries(db_session)
        self._send_anime_reminders(db_session)

        time.sleep(30)

        self._update_manga_entries(db_session)
        self._send_manga_updates(db_session)
