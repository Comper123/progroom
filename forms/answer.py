from wtforms import (
    TextAreaField,
    SubmitField
)
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class AnswerForm(FlaskForm):
    text = TextAreaField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Опубликовать ответ')