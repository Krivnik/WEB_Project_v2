from flask_restful import reqparse, abort, Resource
from . import db_session
from .users import User
from flask import jsonify


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('email', required=True)
parser.add_argument('about', required=True)
parser.add_argument('password', required=True)


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'users': [user.to_dict(only=('name', 'email', 'about'))]})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        abort_if_user_not_found(user_id)
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        user.name = args['name']
        user.email = args['email']
        user.about = args['about']
        user.set_password(args['password'])
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [user.to_dict(only=('name', 'email', 'about'))
                                  for user in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            email=args['email'],
            about=args['about'])
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
