# -*- coding: utf-8 -*-
import unittest
import os

# Adjust path to import app and models
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import create_app
from src.extensions import db
from src.models.user import User


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test variables."""
        # Configure the app for testing
        os.environ["FLASK_ENV"] = "testing"
        # Use an in-memory SQLite database for testing
        os.environ["DB_HOST"] = ""
        os.environ["DB_PORT"] = ""
        os.environ["DB_NAME"] = ""
        os.environ["DB_USERNAME"] = ""
        os.environ["DB_PASSWORD"] = ""
        # Create app with test config
        self.app = create_app()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing forms
        self.app.config["SECRET_KEY"] = "testing-secret-key"
        self.client = self.app.test_client()

        # Create database tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        # Clean up environment variables if needed
        os.environ.pop("FLASK_ENV", None)

    def test_registration_page_loads(self):
        """Test that the registration page loads correctly."""
        response = self.client.get("/auth/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registrar", response.data)

    def test_successful_registration(self):
        """Test user registration."""
        response = self.client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password",
                "password2": "password",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)  # Should redirect to login
        self.assertIn(
            b"Parab\xc3\xa9ns, voc\xc3\xaa foi registrado com sucesso!", response.data
        )  # Check for flash message (bytes)
        # Check if user exists in the database
        with self.app.app_context():
            user = User.query.filter_by(username="testuser").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, "test@example.com")

    def test_login_page_loads(self):
        """Test that the login page loads correctly."""
        response = self.client.get("/auth/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Entrar", response.data)

    def test_successful_login_logout(self):
        """Test user login and logout."""
        # First, register a user
        self.client.post(
            "/auth/register",
            data={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "password",
                "password2": "password",
            },
            follow_redirects=True,
        )

        # Test login
        response = self.client.post(
            "/auth/login",
            data={
                "username": "loginuser",
                "password": "password",
                "remember_me": False,
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)  # Should redirect to index
        self.assertIn(b"Login bem-sucedido! Bem-vindo, loginuser!", response.data)
        self.assertIn(b"Dashboard", response.data)  # Check if redirected to index

        # Test logout
        response = self.client.get("/auth/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)  # Should redirect to login
        self.assertIn(b"Voc\xc3\xaa foi desconectado.", response.data)
        self.assertIn(b"Entrar", response.data)  # Check if redirected to login

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Register a user first
        self.client.post(
            "/auth/register",
            data={
                "username": "invaliduser",
                "email": "invalid@example.com",
                "password": "password",
                "password2": "password",
            },
            follow_redirects=True,
        )

        # Attempt login with wrong password
        response = self.client.post(
            "/auth/login",
            data={
                "username": "invaliduser",
                "password": "wrongpassword",
                "remember_me": False,
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)  # Should stay on login page
        self.assertIn(
            b"Nome de usu\xc3\xa1rio ou senha inv\xc3\xa1lidos", response.data
        )
        self.assertIn(b"Entrar", response.data)


if __name__ == "__main__":
    unittest.main()
