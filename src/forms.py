# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from src.models.user import User


class LoginForm(FlaskForm):
    username = StringField("Nome de Usuário", validators=[DataRequired()])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember_me = BooleanField("Lembrar-me")
    submit = SubmitField("Entrar")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Nome de Usuário", validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        "Repetir Senha",
        validators=[
            DataRequired(),
            EqualTo("password", message="As senhas devem ser iguais."),
        ],
    )
    submit = SubmitField("Registrar")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(
                "Este nome de usuário já está em uso. Por favor, escolha outro."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(
                "Este endereço de email já está em uso. Por favor, escolha outro."
            )
