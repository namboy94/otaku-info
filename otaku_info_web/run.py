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

import os
import base64
import logging
import random
import string
from binascii import Error
from typing import Optional
from flask import render_template, flash, redirect, url_for
from flask.logging import default_handler
from werkzeug.exceptions import HTTPException
from otaku_info_web.config import Config
from otaku_info_web.db.User import User
from otaku_info_web.db.ApiKey import ApiKey
from otaku_info_web.db.models import create_tables
from otaku_info_web.flask import app, db, login_manager
from otaku_info_web.routes.blueprints import register_blueprints


def init_logging():
    """
    Sets up logging
    :return: None
    """
    app.logger.removeHandler(default_handler)
    logging.basicConfig(
        filename=Config().logging_path,
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    app.logger.info("STARTING FLASK")


def init_app():
    """
    Initializes the flask app
    :return: None
    """
    app.testing = os.environ.get("FLASK_TESTING") == "1"
    app.config["TRAP_HTTP_EXCEPTIONS"] = True

    try:
        app.secret_key = os.environ["FLASK_SECRET"]
    except KeyError:
        app.secret_key = "".join(random.choice(string.ascii_letters)
                                 for _ in range(0, 32))
        app.logger.warning("No secret key provided")

    register_blueprints(app)

    @app.context_processor
    def inject_template_variables():
        """
        Injects the project's version string so that it will be available
        in templates
        :return: The dictionary to inject
        """
        return {
            "version": Config().version,
            "env": app.env,
            "config": Config()
        }

    @app.errorhandler(HTTPException)
    def error_handling(error: HTTPException):
        """
        Custom redirect for 401 errors
        :param error: The error that caused the error handler to be called
        :return: A redirect to the login page
        """
        if error.code == 401:
            flash("You are not logged in", "danger")
            return redirect(url_for("user_management.login"))
        else:
            return render_template("static/error_page.html", error=error)

    @app.errorhandler(Exception)
    def exception_handling(e: Exception):
        """
        Handles any uncaught exceptions and shows an error 500 page
        :param e: The caught exception
        :return: None
        """
        error = HTTPException("The server encountered an internal error and "
                              "was unable to complete your request. "
                              "Either the server is overloaded or there "
                              "is an error in the application.")
        error.code = 500
        app.logger.error("Caught exception: {}".format(e))
        return render_template("static/error_page.html", error=error)


def init_db():
    """
    Initializes the database
    :return: None
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = Config().db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Makes sure that we don't get errors because
    # of an idle database connection
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    db.init_app(app)

    create_tables(app, db)


def init_login_manager():
    """
    Initializes the login manager
    :return: None
    """
    login_manager.session_protection = "strong"

    # Set up login manager
    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        """
        Loads a user from an ID
        :param user_id: The ID
        :return: The User
        """
        return User.query.get(int(user_id))

    @login_manager.request_loader
    def load_user_from_request(request) -> Optional[User]:
        """
        Loads a user pased on a provided API key
        :param request: The request containing the API key in the headers
        :return: The user or None if no valid API key was provided
        """
        if "Authorization" not in request.headers:
            return None

        api_key = request.headers["Authorization"].replace("Basic ", "", 1)

        try:
            api_key = base64.b64decode(
                api_key.encode("utf-8")
            ).decode("utf-8")
        except (TypeError, Error):
            return None

        db_api_key = ApiKey.query.get(api_key.split(":", 1)[0])

        # Check for validity of API key
        if db_api_key is None or not db_api_key.verify_key(api_key):
            return None

        elif db_api_key.has_expired():
            db.session.delete(db_api_key)
            db.session.commit()
            return None

        return User.query.get(db_api_key.user_id)


def init():
    """
    Initializes the Flask application
    :return: None
    """
    init_logging()
    init_app()
    init_db()
    init_login_manager()
