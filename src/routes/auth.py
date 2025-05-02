# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from urllib.parse import urlparse

# Import necessary components from the main app structure
from src.extensions import db
from src.models.user import User
from src.forms import LoginForm, RegistrationForm

# Create the blueprint
auth_bp = Blueprint("auth", __name__, template_folder="../static") # Assuming templates are in static for now

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index")) # Redirect if already logged in
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Nome de usuário ou senha inválidos")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        # Redirect to the page the user was trying to access, or index
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        flash(f"Login bem-sucedido! Bem-vindo, {user.username}!")
        return redirect(next_page)
    # Render the login template (assuming it exists in static/)
    return render_template("login.html", title="Entrar", form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Você foi desconectado.")
    return redirect(url_for("auth.login"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Parabéns, você foi registrado com sucesso!")
        return redirect(url_for("auth.login"))
    # Render the registration template (assuming it exists in static/)
    return render_template("register.html", title="Registrar", form=form)

