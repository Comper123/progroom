from wtforms import (
    StringField,
    SubmitField
)
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class SearchForm(FlaskForm):
    query = StringField(validators=[DataRequired()])
    submit = SubmitField('Поиск')