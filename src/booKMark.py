from flask import Blueprint, request, jsonify
import validators
from src.database import BookMark, db
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.constants.http_status_code import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

bookmarks = Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks')

@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def get_bookmarks():

    current_user = get_jwt_identity()

    if request.method == 'POST':
        body = request.get_json().get('body')
        url = request.get_json().get('url')

        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST

        if BookMark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exits'
            }), HTTP_409_CONFLICT

        bookmark = BookMark(
            url=url,
            body=body,
            user_id=current_user
        )

        bookmark.save()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.create_at,
            'updated_at': bookmark.updated_at
        }), HTTP_201_CREATED

    else:
        #getting all bookmarks created by the logged user

        # url pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 3, type=int)

        book_mark = BookMark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)

        data = []

        for bookmark in book_mark.items:
            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'body': bookmark.body,
                'user_id': current_user,
                'created_at': bookmark.create_at,
                'updated_at': bookmark.updated_at
            })

        meta = {
            'page': book_mark.page,
            'per_page': book_mark.per_page,
            'total_count': book_mark.total,
            'prev_page': book_mark.prev_num,
            'next_num': book_mark.next_num,
            'has_next': book_mark.has_next,
            'has_prev': book_mark.has_prev
        }

        return jsonify({
            'data': data,
            'meta': meta
        }), HTTP_200_OK


@bookmarks.get('/<int:id>')
@jwt_required()
def get_one_bookmark(id):

    current_user = get_jwt_identity()

    bookmark = BookMark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'error': "Bookmark not found"}), HTTP_404_NOT_FOUND


    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'user_id': current_user,
        'created_at': bookmark.create_at,
        'updated_at': bookmark.updated_at
    })


@bookmarks.put('/update/<int:id>')
@bookmarks.patch('/update/<int:id>')
@jwt_required()
def update_bookmark(id):

    current_user = get_jwt_identity()

    bookmark = BookMark.query.filter_by(user_id=current_user, id=id).first()

    if not bookmark:
        return jsonify({'error': 'Bookmark do not exist'}), HTTP_404_NOT_FOUND

    body = request.get_json().get('body')
    url = request.get_json().get('url')

    if not validators.url(url):
        return jsonify({'error': 'Enter a valid url'}), HTTP_400_BAD_REQUEST


    bookmark.body = body
    bookmark.url = url

    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.create_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK


@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmarks(id):

    curent_user = get_jwt_identity()

    bookmark = BookMark.query.filter_by(user_id=curent_user, id=id).first()

    if not bookmark:
        return jsonify({'error': 'Bookmark not fount'}), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT

@bookmarks.get('/stats')
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()
    data = []

    items = BookMark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url
        }

        data.append(new_link)

    return jsonify({'data': data}), HTTP_200_OK
