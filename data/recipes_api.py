from flask_restful import reqparse, abort, Resource
from . import db_session
from .recipes import Recipe
from flask import jsonify
from shutil import copyfile
from os import remove


def abort_if_recipe_not_found(recipe_id):
    session = db_session.create_session()
    recipe = session.query(Recipe).get(recipe_id)
    if not recipe:
        abort(404, message=f"Recipe {recipe_id} not found")


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('ingredients', required=True)
parser.add_argument('cooking_time', required=True)
parser.add_argument('content', required=True)
parser.add_argument('image', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


class RecipesResource(Resource):
    def get(self, recipe_id):
        abort_if_recipe_not_found(recipe_id)
        session = db_session.create_session()
        recipe = session.query(Recipe).get(recipe_id)
        return jsonify({'recipes': [recipe.to_dict(only=('title', 'ingredients', 'cooking_time',
                                                         'content', 'user_id', 'is_private'))]})

    def delete(self, recipe_id):
        abort_if_recipe_not_found(recipe_id)
        session = db_session.create_session()
        recipe = session.query(Recipe).get(recipe_id)
        remove(recipe.image)
        session.delete(recipe)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, recipe_id):
        abort_if_recipe_not_found(recipe_id)
        args = parser.parse_args()
        img_name = 'static/img/' + str(recipe_id) + '.' + args['image'].rsplit('.')[-1]
        session = db_session.create_session()
        recipe = session.query(Recipe).get(recipe_id)
        remove(recipe.image)
        recipe.title = args['title']
        recipe.ingredients = args['ingredients']
        recipe.cooking_time = args['cooking_time']
        recipe.content = args['content']
        recipe.image = img_name
        recipe.is_private = args['is_private']
        recipe.user_id = args['user_id']
        copyfile(args['image'], img_name)
        session.commit()
        return jsonify({'success': 'OK'})


class RecipesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        recipes = session.query(Recipe).all()
        return jsonify({'recipes': [recipe.to_dict(
            only=('title', 'ingredients', 'cooking_time', 'content', 'user_id', 'is_private'))
            for recipe in recipes]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        rs = session.query(Recipe).all()
        n = '1' if not rs else str(int(rs[-1].id) + 1)
        img_name = 'static/img/' + n + '.' + args['image'].rsplit('.')[-1]
        recipe = Recipe(
            title=args['title'],
            ingredients=args['ingredients'],
            cooking_time=args['cooking_time'],
            content=args['content'],
            image=img_name,
            is_private=args['is_private'],
            user_id=args['user_id'])
        session.add(recipe)
        copyfile(args['image'], img_name)
        session.commit()
        return jsonify({'success': 'OK'})
