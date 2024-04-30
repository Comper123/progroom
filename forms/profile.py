from wtforms import (
    EmailField, 
    StringField,
    SubmitField
)
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class ProfileForm(FlaskForm):
    name = StringField('Как к вам обращаться?', validators=[DataRequired()])
    email = EmailField('Ваша почта', validators=[DataRequired()])
    submit = SubmitField('Сохранить')