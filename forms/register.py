from wtforms import (
    EmailField, 
    StringField,
    PasswordField, 
    SubmitField
)
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class RegistrationForm(FlaskForm):
    name = StringField('Как к вам обращаться?', validators=[DataRequired()])
    pwd1 = PasswordField('Пароль', validators=[DataRequired()])
    pwd2 = PasswordField('Повторите пароль', validators=[DataRequired()])
    email = EmailField('Ваша почта', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')