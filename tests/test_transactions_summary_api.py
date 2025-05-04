# -*- coding: utf-8 -*-
import pytest
from flask import Flask, jsonify
from flask.testing import FlaskClient
from datetime import date, timedelta
from decimal import Decimal

# Assuming your Flask app instance is created in src.main or similar
# and configured for testing (e.g., using a test database)
from src.main import create_app # Adjust import based on your app structure
from src.extensions import db
from src.models.user import User
from src.models.account import Account
from src.models.category import Category
from src.models.transaction import Transaction, TRANSACTION_TYPE_DESPESA, TRANSACTION_TYPE_RECEITA

@pytest.fixture(scope=\"module\")
def test_client() -> FlaskClient:
    """Fixture to create a test client for the Flask app."""
    flask_app = create_app(config_name=\"testing\") # Use a testing configuration

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            db.create_all() # Create tables for the test database
            # Create necessary seed data (user, accounts, categories)
            seed_data()
            yield testing_client # this is where the testing happens!
            db.session.remove()
            db.drop_all() # Clean up the database

def seed_data():
    """Helper function to seed the test database."""
    # Create a test user
    test_user = User(username=\"testuser\", email=\"test@example.com\")
    test_user.set_password(\"password\")
    db.session.add(test_user)
    db.session.commit()

    # Create accounts
    acc1 = Account(user_id=test_user.id, name=\"Conta Corrente\")
    acc2 = Account(user_id=test_user.id, name=\"Carteira\")
    db.session.add_all([acc1, acc2])
    db.session.commit()

    # Create categories
    cat_salario = Category(user_id=test_user.id, name=\"Salário\", type=TRANSACTION_TYPE_RECEITA)
    cat_alimentacao = Category(user_id=test_user.id, name=\"Alimentação\", type=TRANSACTION_TYPE_DESPESA)
    cat_transporte = Category(user_id=test_user.id, name=\"Transporte\", type=TRANSACTION_TYPE_DESPESA)
    db.session.add_all([cat_salario, cat_alimentacao, cat_transporte])
    db.session.commit()

    # Create transactions
    today = date.today()
    yesterday = today - timedelta(days=1)
    last_month_date = today - timedelta(days=30)

    t1 = Transaction(user_id=test_user.id, account_id=acc1.id, category_id=cat_salario.id, amount=Decimal(\"5000.00\"), type=TRANSACTION_TYPE_RECEITA, date=last_month_date, description=\"Salário Mês Passado\")
    t2 = Transaction(user_id=test_user.id, account_id=acc1.id, category_id=cat_alimentacao.id, amount=Decimal(\"150.50\"), type=TRANSACTION_TYPE_DESPESA, date=yesterday, description=\"Almoço\")
    t3 = Transaction(user_id=test_user.id, account_id=acc2.id, category_id=cat_transporte.id, amount=Decimal(\"50.00\"), type=TRANSACTION_TYPE_DESPESA, date=today, description=\"Ônibus\", is_paid=False)
    t4 = Transaction(user_id=test_user.id, account_id=acc1.id, category_id=cat_alimentacao.id, amount=Decimal(\"25.00\"), type=TRANSACTION_TYPE_DESPESA, date=today, description=\"Café\")
    db.session.add_all([t1, t2, t3, t4])
    db.session.commit()

def login(client: FlaskClient, username=\"testuser\", password=\"password\"):
    """Helper function to log in the test user."""
    return client.post(\"/auth/login\", data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

# --- Test Transactions API --- (CRUD)

def test_api_list_transactions_unauthorized(test_client: FlaskClient):
    """Test listing transactions without login."""
    response = test_client.get(\"/transactions/api\")
    # Expect redirect to login or 401 depending on Flask-Login config
    assert response.status_code in [302, 401]

def test_api_list_transactions_authorized(test_client: FlaskClient):
    """Test listing transactions after login."""
    login(test_client)
    response = test_client.get(\"/transactions/api\")
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) >= 4 # Based on seed data
    assert json_data[0][\"description\"] == \"Café\" # Most recent

def test_api_get_single_transaction(test_client: FlaskClient):
    """Test getting a single transaction by ID."""
    login(test_client)
    # Find a transaction ID from the seeded data
    trans = Transaction.query.filter_by(description=\"Almoço\").first()
    assert trans is not None

    response = test_client.get(f\"/transactions/api/{trans.id}\")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data[\"id\"] == trans.id
    assert json_data[\"description\"] == \"Almoço\"
    assert json_data[\"amount\"] == \"150.50\"

def test_api_get_single_transaction_not_found(test_client: FlaskClient):
    """Test getting a non-existent transaction."""
    login(test_client)
    response = test_client.get(\"/transactions/api/99999\")
    assert response.status_code == 404
    assert \"error\" in response.get_json()

def test_api_add_transaction(test_client: FlaskClient):
    """Test adding a new transaction via API."""
    login(test_client)
    account = Account.query.filter_by(name=\"Conta Corrente\").first()
    category = Category.query.filter_by(name=\"Alimentação\").first()
    assert account is not None
    assert category is not None

    new_trans_data = {
        \"type\": TRANSACTION_TYPE_DESPESA,
        \"description\": \"Jantar Teste\",
        \"amount\": \"75.99\",
        \"date\": date.today().isoformat(),
        \"account_id\": account.id,
        \"category_id\": category.id,
        \"is_paid\": True
    }
    response = test_client.post(\"/transactions/api\", json=new_trans_data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data[\"description\"] == \"Jantar Teste\"
    assert json_data[\"amount\"] == \"75.99\"
    assert \"id\" in json_data

    # Verify it was added to the DB
    added_trans = Transaction.query.get(json_data[\"id\"])
    assert added_trans is not None
    assert added_trans.description == \"Jantar Teste\"

def test_api_add_transaction_invalid_data(test_client: FlaskClient):
    """Test adding a transaction with invalid data."""
    login(test_client)
    response = test_client.post(\"/transactions/api\", json={\"amount\": \"abc\"}) # Missing fields, invalid amount
    assert response.status_code == 400
    assert \"error\" in response.get_json()

def test_api_edit_transaction(test_client: FlaskClient):
    """Test editing an existing transaction via API (PUT/PATCH)."""
    login(test_client)
    trans_to_edit = Transaction.query.filter_by(description=\"Café\").first()
    assert trans_to_edit is not None

    edit_data = {\"description\": \"Café Expresso\", \"amount\": \"30.00\"}
    response = test_client.patch(f\"/transactions/api/{trans_to_edit.id}\", json=edit_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data[\"description\"] == \"Café Expresso\"
    assert json_data[\"amount\"] == \"30.00\"

    # Verify change in DB
    edited_trans = Transaction.query.get(trans_to_edit.id)
    assert edited_trans.description == \"Café Expresso\"
    assert edited_trans.amount == Decimal(\"30.00\")

def test_api_delete_transaction(test_client: FlaskClient):
    """Test deleting a transaction via API."""
    login(test_client)
    # Add a temporary transaction to delete
    account = Account.query.first()
    category = Category.query.filter_by(type=TRANSACTION_TYPE_DESPESA).first()
    temp_trans = Transaction(user_id=User.query.first().id, account_id=account.id, category_id=category.id, amount=Decimal(\"10.00\"), type=TRANSACTION_TYPE_DESPESA, date=date.today(), description=\"ToDelete\")
    db.session.add(temp_trans)
    db.session.commit()
    trans_id_to_delete = temp_trans.id

    response = test_client.delete(f\"/transactions/api/{trans_id_to_delete}\")
    assert response.status_code == 200
    assert \"message\" in response.get_json()

    # Verify deletion from DB
    deleted_trans = Transaction.query.get(trans_id_to_delete)
    assert deleted_trans is None

# --- Test Summary API ---

def test_api_get_balance(test_client: FlaskClient):
    """Test getting the overall balance."""
    login(test_client)
    response = test_client.get(\"/summary/api/balance\")
    assert response.status_code == 200
    json_data = response.get_json()
    assert \"balance\" in json_data
    # Calculate expected balance based on seed data (adjust if seed data changes)
    # Salário (5000) - Almoço (150.50) - Ônibus (50.00) - Café (25.00) = 4774.50
    assert Decimal(json_data[\"balance\"]) == Decimal(\"4774.50\")

def test_api_get_monthly_summary(test_client: FlaskClient):
    """Test getting the monthly summary for the current month."""
    login(test_client)
    today = date.today()
    response = test_client.get(f\"/summary/api/monthly?year={today.year}&month={today.month}\")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data[\"year\"] == today.year
    assert json_data[\"month\"] == today.month
    assert \"total_income\" in json_data
    assert \"total_expense\" in json_data
    # Based on seed data for today: Income=0, Expense=50.00(Ônibus)+25.00(Café)=75.00
    assert Decimal(json_data[\"total_income\"]) == Decimal(\"0.00\")
    assert Decimal(json_data[\"total_expense\"]) == Decimal(\"75.00\")
    assert Decimal(json_data[\"monthly_balance\"]) == Decimal(\"-75.00\")

def test_api_get_monthly_summary_last_month(test_client: FlaskClient):
    """Test getting the monthly summary for the previous month."""
    login(test_client)
    last_month_dt = date.today() - timedelta(days=30)
    response = test_client.get(f\"/summary/api/monthly?year={last_month_dt.year}&month={last_month_dt.month}\")
    assert response.status_code == 200
    json_data = response.get_json()
    # Based on seed data for last month: Income=5000, Expense=0
    assert Decimal(json_data[\"total_income\"]) == Decimal(\"5000.00\")
    assert Decimal(json_data[\"total_expense\"]) == Decimal(\"0.00\")
    assert Decimal(json_data[\"monthly_balance\"]) == Decimal(\"5000.00\")

def test_api_get_pending_summary(test_client: FlaskClient):
    """Test getting the summary of pending transactions."""
    login(test_client)
    response = test_client.get(\"/summary/api/pending\")
    assert response.status_code == 200
    json_data = response.get_json()
    # Based on seed data: 1 pending expense (Ônibus 50.00), 0 pending income
    assert \"total_pending_expenses\" in json_data
    assert \"count_pending_expenses\" in json_data
    assert \"total_pending_income\" in json_data
    assert \"count_pending_income\" in json_data
    assert Decimal(json_data[\"total_pending_expenses\"]) == Decimal(\"50.00\")
    assert json_data[\"count_pending_expenses\"] == 1
    assert Decimal(json_data[\"total_pending_income\"]) == Decimal(\"0.00\")
    assert json_data[\"count_pending_income\"] == 0

