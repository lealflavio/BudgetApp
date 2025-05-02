# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions globally
db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login" # Default route for login
migrate = Migrate()

