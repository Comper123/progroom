from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    SelectField
)
from wtforms.fields import FileField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from data import db_session, theme


class QuestionForm(FlaskForm):
    title = StringField('Вопрос: ', validators=[DataRequired()])
    content = TextAreaField('Описание проблемы', validators=[DataRequired()])
    db_session.global_init('db/forum.db')
    theme = SelectField('Тема вопроса', choices=[t.title for t in db_session.create_session().query(theme.Theme).all()])
    img = FileField('Фотография')
    submit = SubmitField('Опубликовать вопрос')

