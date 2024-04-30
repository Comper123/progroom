from wtforms import (
    EmailField, 
    PasswordField, 
    SubmitField,
    BooleanField
)
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('запомнить меня')
    
    submit = SubmitField('Войти')