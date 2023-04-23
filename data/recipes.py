from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Recipe(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'recipes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ingredients = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # потом объясню реализацию
    cooking_time = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    user = orm.relationship('User')
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
