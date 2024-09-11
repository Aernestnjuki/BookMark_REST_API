from flask import Flask, redirect, jsonify
from dotenv import load_dotenv
import os
from src.auth import auth
from src.booKMark import bookmarks
from src.constants.http_status_code import HTTP_404_NOT_FOUND
from src.database import db, BookMark
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


    # incrementing the visits
    @app.get('/<short_url>')
    def redirect_to_url(short_url):
        bookmark = BookMark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits+1
            db.session.commit()

        return redirect(bookmark.url) # redirect to the url in the database


    # error handling
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': "Not Found"}), HTTP_404_NOT_FOUND


    @app.errorhandler(500)
    def server_error_handler(e):
        return jsonify({'error': 'something went wrong'}), 500 # internal server error

    return app