from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class ThemeForm(FlaskForm):
    title = StringField('Название темы: ', validators=[DataRequired()])
    description = TextAreaField('Описание темы', validators=[DataRequired()])
    submit = SubmitField('Создать тему')