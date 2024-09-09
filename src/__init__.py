from flask import Flask
from dotenv import load_dotenv
import os
from src.auth import auth
from src.booKMark import bookmarks
from src.database import db
from flask_jwt_extended import JWTManager

load_dotenv()


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True # tells flask that there will be more configurations
    )

    if test_config is None:

        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
        )
    else:
        app.config.from_mapping(test_config)



    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    return app