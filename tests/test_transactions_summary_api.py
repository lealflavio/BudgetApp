# -*- coding: utf-8 -*-
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_login import login_user, logout_user
from decimal import Decimal
from datetime import date

from src.main import create_app # Assuming create_app is in src.main
from src.extensions import db
from src.models.user import User
from src.models.account import Account
from src.models.category import Category
from src.models.transaction import Transaction, TRANSACTION_TYPE_DESPESA, TRANSACTION_TYPE_RECEITA

# --- Fixtures ---
@pytest.fixture(scope='module')
def test_app():
    """Create and configure a new app instance for each test module."""
    app = create_app(testing=True) # Use a testing configuration
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app: Flask) -> FlaskClient:
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture(scope='function') # Use function scope to ensure clean state for each test
def logged_in_user(test_app: Flask) -> User:
    """Create and log in a user."""
    with test_app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        # Simulate login within the request context if needed by routes
        # For API tests, we might just need the user object for ID
        yield user
        # Clean up user and related data after test
        # Cascading deletes should handle related items if configured
        db.session.delete(user)
        db.session.commit()

@pytest.fixture(scope='function')
def test_data(test_app: Flask, logged_in_user: User):
    """Create sample accounts, categories, and transactions."""
    with test_app.app_context():
        acc1 = Account(user_id=logged_in_user.id, name="Conta Corrente", type="Corrente", initial_balance=1000.00)
        acc2 = Account(user_id=logged_in_user.id, name="Cartão Crédito", type="Crédito", initial_balance=0.00)
        cat_salario = Category(user_id=logged_in_user.id, name="Salário", type=TRANSACTION_TYPE_RECEITA)
        cat_alimentacao = Category(user_id=logged_in_user.id, name="Alimentação", type=TRANSACTION_TYPE_DESPESA)
        cat_transporte = Category(user_id=logged_in_user.id, name="Transporte", type=TRANSACTION_TYPE_DESPESA)
        cat_default_lazer = Category(name="Lazer", type=TRANSACTION_TYPE_DESPESA, is_default=True)

        db.session.add_all([acc1, acc2, cat_salario, cat_alimentacao, cat_transporte, cat_default_lazer])
        db.session.commit()

        # Transactions for month 1
        t1 = Transaction(user_id=logged_in_user.id, account_id=acc1.id, category_id=cat_salario.id, amount=5000.00, type=TRANSACTION_TYPE_RECEITA, date=date(2025, 1, 5))
        t2 = Transaction(user_id=logged_in_user.id, account_id=acc1.id, category_id=cat_alimentacao.id, amount=350.50, type=TRANSACTION_TYPE_DESPESA, date=date(2025, 1, 10))
        t3 = Transaction(user_id=logged_in_user.id, account_id=acc2.id, category_id=cat_transporte.id, amount=80.00, type=TRANSACTION_TYPE_DESPESA, date=date(2025, 1, 15))
        t4 = Transaction(user_id=logged_in_user.id, account_id=acc1.id, category_id=cat_default_lazer.id, amount=120.00, type=TRANSACTION_TYPE_DESPESA, date=date(2025, 1, 20), is_paid=False) # Pending

        # Transactions for month 2
        t5 = Transaction(user_id=logged_in_user.id, account_id=acc1.id, category_id=cat_salario.id, amount=5100.00, type=TRANSACTION_TYPE_RECEITA, date=date(2025, 2, 5))
        t6 = Transaction(user_id=logged_in_user.id, account_id=acc1.id, category_id=cat_alimentacao.id, amount=400.00, type=TRANSACTION_TYPE_DESPESA, date=date(2025, 2, 12))

        db.session.add_all([t1, t2, t3, t4, t5, t6])
        db.session.commit()

        return {
            "user": logged_in_user,
            "acc1": acc1,
            "acc2": acc2,
            "cat_salario": cat_salario,
            "cat_alimentacao": cat_alimentacao,
            "cat_transporte": cat_transporte,
            "cat_default_lazer": cat_default_lazer,
            "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5, "t6": t6
        }

# --- Helper Function for Logged-in Requests ---
def login(client: FlaskClient, user: User):
    # Use the client's session handling or a token mechanism if implemented
    # For basic Flask-Login session:
    with client.session_transaction() as sess:
        # This might not work directly if login_user needs request context
        # A common pattern is to post to a login route first
        pass # Placeholder - Actual login simulation depends on auth setup
    # Alternative: If using request hooks or context processors for user loading,
    # ensure the user is available in the context for the test request.
    # For API tests, often just knowing the user ID is enough for filtering.
    # We will rely on the user_id being available via current_user mock or fixture.

# --- Test Cases ---

# Test Summary API
def test_get_monthly_summary_api(test_client: FlaskClient, test_data):
    user = test_data["user"]
    # Simulate login if required by the endpoint decorator
    # For now, assume user context is handled (e.g., via test request user)

    # Test Month 1 (Jan 2025)
    response = test_client.get(f"/summary/api/monthly?year=2025&month=1", headers={"X-Test-User-Id": str(user.id)}) # Pass user ID if needed
    assert response.status_code == 200
    data = response.get_json()
    assert data["year"] == 2025
    assert data["month"] == 1
    assert Decimal(data["total_income"]) == Decimal("5000.00")
    assert Decimal(data["total_expenses"]) == Decimal("350.50") + Decimal("80.00") + Decimal("120.00") # Includes pending
    assert Decimal(data["month_balance"]) == Decimal("5000.00") - (Decimal("350.50") + Decimal("80.00") + Decimal("120.00"))
    # Assuming initial balance = 0 and no prior transactions
    assert Decimal(data["balance_at_start"]) == Decimal("0.00")
    assert Decimal(data["balance_at_end"]) == Decimal(data["month_balance"])

    # Test Month 2 (Feb 2025)
    response = test_client.get(f"/summary/api/monthly?year=2025&month=2", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 200
    data = response.get_json()
    assert data["year"] == 2025
    assert data["month"] == 2
    assert Decimal(data["total_income"]) == Decimal("5100.00")
    assert Decimal(data["total_expenses"]) == Decimal("400.00")
    assert Decimal(data["month_balance"]) == Decimal("5100.00") - Decimal("400.00")
    # Balance at start of Feb should be balance at end of Jan
    assert Decimal(data["balance_at_start"]) == Decimal("5000.00") - (Decimal("350.50") + Decimal("80.00") + Decimal("120.00"))
    assert Decimal(data["balance_at_end"]) == Decimal(data["balance_at_start"]) + Decimal(data["month_balance"])

    # Test Invalid Month
    response = test_client.get(f"/summary/api/monthly?year=2025&month=13", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 400

def test_get_pending_summary_api(test_client: FlaskClient, test_data):
    user = test_data["user"]
    response = test_client.get(f"/summary/api/pending", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 200
    data = response.get_json()
    assert Decimal(data["pending_expenses_total"]) == Decimal("120.00")
    assert data["pending_expenses_count"] == 1
    assert Decimal(data["pending_income_total"]) == Decimal("0.00")
    assert data["pending_income_count"] == 0

# Test Transactions API
def test_list_transactions_api(test_client: FlaskClient, test_data):
    user = test_data["user"]
    response = test_client.get("/transactions/api", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 6 # 4 in Jan, 2 in Feb
    # Check if one of the transactions matches expected data
    assert any(t["id"] == test_data["t1"].id and Decimal(t["amount"]) == Decimal("5000.00") for t in data)

def test_get_single_transaction_api(test_client: FlaskClient, test_data):
    user = test_data["user"]
    t2_id = test_data["t2"].id
    response = test_client.get(f"/transactions/api/{t2_id}", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == t2_id
    assert data["description"] == test_data["t2"].description
    assert Decimal(data["amount"]) == test_data["t2"].amount

    # Test Not Found
    response = test_client.get("/transactions/api/9999", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 404

def test_add_transaction_api(test_client: FlaskClient, test_data):
    user = test_data["user"]
    acc1_id = test_data["acc1"].id
    cat_alimentacao_id = test_data["cat_alimentacao"].id

    new_trans_data = {
        "type": TRANSACTION_TYPE_DESPESA,
        "amount": "55.75",
        "date": "2025-02-20",
        "account_id": acc1_id,
        "category_id": cat_alimentacao_id,
        "description": "Lanche tarde"
    }
    response = test_client.post("/transactions/api", json=new_trans_data, headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 201
    data = response.get_json()
    assert data["description"] == "Lanche tarde"
    assert Decimal(data["amount"]) == Decimal("55.75")
    assert data["account_id"] == acc1_id

    # Test validation error (negative amount)
    invalid_data = new_trans_data.copy()
    invalid_data["amount"] = "-10.00"
    response = test_client.post("/transactions/api", json=invalid_data, headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 400

    # Test validation error (missing field)
    invalid_data = new_trans_data.copy()
    del invalid_data["account_id"]
    response = test_client.post("/transactions/api", json=invalid_data, headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 400

    # Test validation error (category type mismatch)
    invalid_data = new_trans_data.copy()
    invalid_data["category_id"] = test_data["cat_salario"].id # Salario is Receita
    response = test_client.post("/transactions/api", json=invalid_data, headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 400

def test_edit_transaction_api(test_client: FlaskClient, test_data):
    user = test_data["user"]
    t3_id = test_data["t3"].id
    acc1_id = test_data["acc1"].id

    update_data = {
        "description": "Uber Viagem",
        "amount": "85.50",
        "account_id": acc1_id # Change account
    }
    response = test_client.put(f"/transactions/api/{t3_id}", json=update_data, headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == t3_id
    assert data["description"] == "Uber Viagem"
    assert Decimal(data["amount"]) == Decimal("85.50")
    assert data["account_id"] == acc1_id

    # Test edit not found
    response = test_client.put("/transactions/api/9999", json=update_data, headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 404

    # Test validation error (change type without changing category)
    update_data_invalid = {"type": TRANSACTION_TYPE_RECEITA}
    response = test_client.put(f"/transactions/api/{t3_id}", json=update_data_invalid, headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 400

def test_delete_transaction_api(test_client: FlaskClient, test_data):
    user = test_data["user"]
    t6_id = test_data["t6"].id

    response = test_client.delete(f"/transactions/api/{t6_id}", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 200
    data = response.get_json()
    assert "success" in data["message"].lower()

    # Verify it's deleted
    response = test_client.get(f"/transactions/api/{t6_id}", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 404

    # Test delete not found
    response = test_client.delete("/transactions/api/9999", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 404

def test_get_categories_for_form_api(test_client: FlaskClient, test_data):
    user = test_data["user"]

    # Test Despesa
    response = test_client.get(f"/transactions/_get_categories/{TRANSACTION_TYPE_DESPESA}", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 3 # Alimentacao, Transporte, Lazer (default)
    assert any(c["name"] == "Alimentação" for c in data)
    assert any(c["name"] == "Lazer" for c in data)

    # Test Receita
    response = test_client.get(f"/transactions/_get_categories/{TRANSACTION_TYPE_RECEITA}", headers={"X-Test-User-Id": str(user.id)})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(c["name"] == "Salário" for c in data)


