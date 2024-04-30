import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'
    # Параметры пользователя
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_superuser = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    lvl = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    exp = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    # Внешние связи
    question = orm.relationship("Question", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    def give_experience(self, exp: int):
        self.exp += exp
        self.lvl = min(self.exp // 100 + 1, 27)
    
    def take_experience(self, exp: int):
        self.exp -= exp
        self.lvl = min(self.exp // 100 + 1, 27)