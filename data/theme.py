import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
import datetime


class Theme(SqlAlchemyBase):
    __tablename__ = 'themes'
    # Параметры темы
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    creator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    
    # Внешние связи
    user = orm.relationship("User")
