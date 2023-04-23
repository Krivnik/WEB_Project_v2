from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, \
    TextAreaField, SubmitField, \
    EmailField, BooleanField, \
    TimeField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EditForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    password = PasswordField('Подтвердите пароль', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')


class RecipeForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    ingredient1, ingredient2, ingredient3, ingredient4, ingredient5,\
        ingredient6, ingredient7, ingredient8, ingredient9, ingredient10,\
        ingredient11, ingredient12, ingredient13, ingredient14, ingredient15 \
        = (BooleanField(text) for text in
           ['Мясо', 'Птица', 'Рыба/Морепродукты', 'Рис', 'Макароны',
            'Гречневая крупа', 'Картофель', 'Лук', 'Морковь', 'Томаты',
            'Перец сладкий', 'Грибы', 'Бобовые', 'Орехи', 'Фрукты/ягоды'])
    cooking_time = TimeField('Время приготовления', validators=[DataRequired()])
    content = TextAreaField("Рецепт", validators=[DataRequired()])
    image = FileField('Изображение', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
