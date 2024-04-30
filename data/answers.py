import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
import datetime
from sqlalchemy_serializer import SerializerMixin


class Answer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'answers'

    # Параметры ответа
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_like_autor = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    autor = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    question = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("questions.id"))
    like_users = sqlalchemy.Column(sqlalchemy.String, default='0')

    # Внешние связи
    user = orm.relationship("User")
    ques = orm.relationship("Question")

    def liked(self):
        return list(map(int, self.like_users.split(',')))
    
    def like(self, user_id: int):
        self.like_users = self.like_users + f',{user_id}'

    def dislike(self, user_id: int):
        self.like_users = self.like_users.replace(f',{user_id}', '')