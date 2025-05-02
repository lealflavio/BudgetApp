# -*- coding: utf-8 -*-
import pytest
from src.main import create_app # Assuming your Flask app factory is in src/main.py
from src.extensions import db
from src.models.user import User
from src.models.account import Account
from src.models.category import Category

@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask application."""
    # Use a testing configuration
    # You might need to create a config.py or similar with a TestingConfig class
    # For simplicity, using in-memory SQLite for tests
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use in-memory SQLite for tests
        "WTF_CSRF_ENABLED": False, # Disable CSRF for testing forms/APIs easily
        "SECRET_KEY": "test-secret-key",
        "LOGIN_DISABLED": True # Optional: Disable login requirement for some tests if needed
                               # Or handle login within tests
    }
    _app = create_app(config_override=config)

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """Create the database tables for each test."""
    with app.app_context():
        db.create_all()
        yield db # Provide the db object to tests
        db.drop_all()

@pytest.fixture(scope='function')
def logged_in_user(app, init_database):
    """Creates and logs in a user for tests requiring authentication."""
    with app.app_context():
        # Create a user
        user = User(username="testuser", email="test@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()

        # Simulate login (adjust based on your actual login mechanism)
        # If using Flask-Login, you might need to push a user into the session
        # For API tests, we often rely on the user_id being available (e.g., via @login_required)
        # Since LOGIN_DISABLED=True might be set, or we mock current_user
        # Here, we just return the created user object for reference in tests
        # The @login_required decorator might need adjustment or mocking in a real scenario
        # or ensure the test client handles sessions correctly.
        # For simplicity in this example, we assume current_user will work correctly
        # because the user exists in the DB and we might rely on test client session handling
        # or direct mocking if needed.

        # A more robust way for API tests might involve generating a token
        # or setting session cookies if your auth works that way.
        # Let's assume for now that having the user in the DB is sufficient
        # for the mocked @login_required to find current_user.id
        return user

