from flask import Flask
import os
from src.auth import auth
from src.booKMark import bookmarks
from src.database import db


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True # tells flask that there will be more configurations
    )

    if test_config is None:

        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI')
        )
    else:
        app.config.from_mapping(test_config)


    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    return app