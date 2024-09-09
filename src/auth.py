from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.constants.http_status_code import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED
import validators
from src.database import User
from flask_jwt_extended import create_access_token, create_refresh_token

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.post('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password) < 6:
        return jsonify({'error': 'password is too short!'}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': 'username is too short!'}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': 'Your email is not valid'}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'This email already exits'}), HTTP_409_CONFLICT # meaning something already exits hence a conflict

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'This username already exits'}), HTTP_409_CONFLICT

    password_hash = generate_password_hash(password)

    user = User(
        username = username,
        email = email,
        password = password_hash
    )

    user.save()


    return jsonify({
        'message': "Successful",
        'user': {
            'username': username,
            'email': email
        }
    }), HTTP_201_CREATED


@auth.post('/login')
def login():
    email = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'user': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'username': user.username,
                'email': user.email
            }
        }), HTTP_200_OK

    return jsonify({'error': 'Wrong email or username!'}), HTTP_401_UNAUTHORIZED