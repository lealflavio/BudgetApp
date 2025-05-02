# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, redirect, url_for, flash, request
from urllib.parse import urlparse

# Import extensions from the dedicated file
from src.extensions import db, login, migrate

# DO NOT import forms or models here at the top level

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="static")
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "you-will-never-guess") # Use environment variable in production

    # Configure database
    db_user = os.getenv("DB_USERNAME", "root")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "mydb")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions with app
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)

    # Import models HERE, inside create_app, after db is initialized
    from src.models.user import User
    from src.models.account import Account
    from src.models.category import Category
    from src.models.transaction import Transaction

    # User loader needs User model
    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Import forms HERE, inside create_app
    from src.forms import LoginForm, RegistrationForm

    # Register Blueprints HERE, inside create_app
    from src.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from src.routes.accounts import accounts_bp
    app.register_blueprint(accounts_bp)

    from src.routes.categories import categories_bp
    app.register_blueprint(categories_bp)

    from src.routes.transactions import transactions_bp
    app.register_blueprint(transactions_bp)

    from src.routes.summary import summary_bp
    app.register_blueprint(summary_bp)

    # --- Main Routes (Example) ---
    @app.route("/")
    @app.route("/index")
    @login_required # Protect the index page
    def index():
        # Replace with actual dashboard logic later
        return render_template("index.html", title="Dashboard")

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        try:
            db.session.rollback()
        except Exception as e:
            app.logger.error(f"Error rolling back session: {e}")
        return render_template("500.html"), 500

    return app

# Create the main app instance (for running locally)
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

