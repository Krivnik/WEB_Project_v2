from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_restful import Api
from data import db_session, recipes_api, users_api
from data.users import User
from data.recipes import Recipe
from forms.user import RegisterForm, LoginForm, EditForm, RecipeForm, SearchForm
from os import remove, environ
from datetime import time
from PIL import Image

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', form=form, message="Неправильный логин или пароль")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if request.method == "GET":
        form.name.data = current_user.name
        form.about.data = current_user.about
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            return render_template('edit.html', title='Редактирование данных', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        user.name = form.name.data
        user.about = form.about.data
        db_sess.commit()
        return redirect('/')
    return render_template('edit.html', title='Редактирование данных', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/recipes', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        if request.files['image'].filename.rsplit('.')[-1] not in ['jpg', 'jpeg', 'png', 'bmp']:
            return render_template('recipe.html', title='Добавление рецепта', form=form,
                                   message='Выбранный файл не является изображением, '
                                           'либо не поддерживается сайтом')
        ingredients = [form.ingredient1, form.ingredient2, form.ingredient3, form.ingredient4,
                       form.ingredient5, form.ingredient6, form.ingredient7, form.ingredient8,
                       form.ingredient9, form.ingredient10, form.ingredient11, form.ingredient12,
                       form.ingredient13, form.ingredient14, form.ingredient15]
        db_sess = db_session.create_session()
        rs = db_sess.query(Recipe).all()
        n = '1' if not rs else str(int(rs[-1].id) + 1)
        img_name = 'static/img/' + n + '.' + request.files['image'].filename.rsplit('.')[-1]
        recipe = Recipe(
            title=form.title.data,
            ingredients=''.join([str(int(i.data)) for i in ingredients]),
            cooking_time=form.cooking_time.data.isoformat(timespec='minutes'),
            content=form.content.data,
            image=img_name,
            user_id=current_user.id)
        db_sess.add(recipe)
        request.files['image'].save(img_name)
        img = Image.open(img_name)
        img.thumbnail(size=(525, 525))
        img.save(img_name)
        db_sess.commit()
        return redirect('/')
    return render_template('recipe.html', title='Добавление рецепта', form=form)


@app.route('/recipes/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_recipe(id):
    form = RecipeForm()
    ingredients = [form.ingredient1, form.ingredient2, form.ingredient3, form.ingredient4,
                   form.ingredient5, form.ingredient6, form.ingredient7, form.ingredient8,
                   form.ingredient9, form.ingredient10, form.ingredient11, form.ingredient12,
                   form.ingredient13, form.ingredient14, form.ingredient15]
    if request.method == "GET":
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipe).filter(Recipe.id == id,
                                              Recipe.user_id == current_user.id).first()
        if recipe:
            form.title.data = recipe.title
            for i in range(len(ingredients)):
                ingredients[i].data = int(recipe.ingredients[i])
            form.cooking_time.data = time(*tuple([int(i) for i in recipe.cooking_time.split(':')]))
            form.content.data = recipe.content
        else:
            abort(404)
    if form.validate_on_submit():
        if request.files['image'].filename.rsplit('.')[-1] not in ['jpg', 'jpeg', 'png', 'bmp']:
            return render_template('recipe.html', title='Добавление рецепта', form=form,
                                   message='Выбранный файл не является изображением, '
                                           'либо не поддерживается сайтом')
        db_sess = db_session.create_session()
        recipe = db_sess.query(Recipe).filter(Recipe.id == id,
                                              Recipe.user_id == current_user.id).first()
        img_name = \
            recipe.image.rsplit('.')[0] + '.' + request.files['image'].filename.rsplit('.')[-1]
        if recipe:
            remove(recipe.image)
            recipe.title = form.title.data
            recipe.ingredients = ''.join([str(int(i.data)) for i in ingredients])
            recipe.cooking_time = form.cooking_time.data.isoformat(timespec='minutes')
            recipe.content = form.content.data
            recipe.image = img_name
            request.files['image'].save(img_name)
            img = Image.open(img_name)
            img.thumbnail(size=(525, 525))
            img.save(img_name)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('recipe.html', title='Редактирование рецепта', form=form)


@app.route('/recipes_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def recipe_delete(id):
    db_sess = db_session.create_session()
    recipe = db_sess.query(Recipe).filter(Recipe.id == id, Recipe.user_id == current_user.id).first()
    if recipe:
        db_sess.delete(recipe)
        remove(recipe.image)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        ingredients = [form.ingredient1, form.ingredient2, form.ingredient3, form.ingredient4,
                       form.ingredient5, form.ingredient6, form.ingredient7, form.ingredient8,
                       form.ingredient9, form.ingredient10, form.ingredient11, form.ingredient12,
                       form.ingredient13, form.ingredient14, form.ingredient15]
        return redirect(f"/search/{form.title.data}."
                        f"{''.join([str(int(i.data)) for i in ingredients])}")
    return render_template('search.html', title='Поиск', form=form)


@app.route('/search/<string:title>.<string:ingredients>')
def show_results(title, ingredients):
    ingredients = ''.join(['_' if i == '0' else '1' for i in ingredients])
    db_sess = db_session.create_session()
    recipes = db_sess.query(Recipe).filter(Recipe.title.like(f'%{title}%'),
                                           Recipe.ingredients.like(ingredients)).all()
    return render_template('index.html', title='Результаты поиска', recipes=recipes,
                           undertitle='Результаты поиска')


@app.route('/')
def index():
    db_sess = db_session.create_session()
    recipes = reversed(db_sess.query(Recipe).all())
    return render_template('index.html', title='Главная', recipes=recipes,
                           undertitle='Последние рецепты')


@app.route('/about')
def about():
    return render_template('about.html', title='О нас')


def main():
    db_session.global_init("db/recipes.db")
    api.add_resource(recipes_api.RecipesListResource, '/api/recipes')
    api.add_resource(recipes_api.RecipesResource, '/api/recipes/<int:recipe_id>')
    api.add_resource(users_api.UsersListResource, '/api/users')
    api.add_resource(users_api.UsersResource, '/api/users/<int:user_id>')
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
