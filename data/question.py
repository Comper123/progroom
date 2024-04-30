import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
import datetime


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'
    # Параметры вопроса
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    img = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_answer = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_delete = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    autor = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    theme_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("themes.id"))
    
    # Внешние связи
    user = orm.relationship("User")
    theme = orm.relationship("Theme")
