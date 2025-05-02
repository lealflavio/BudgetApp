# -*- coding: utf-8 -*-
import json
from decimal import Decimal
from src.models.account import Account

def test_list_accounts_empty(client, logged_in_user):
    """Test listing accounts when none exist for the user."""
    res = client.get("/accounts")
    assert res.status_code == 200
    assert res.json == []

def test_add_account_success(client, logged_in_user, init_database):
    """Test successfully adding a new account."""
    data = {
        "name": "Conta Corrente Principal",
        "type": "Conta Corrente",
        "initial_balance": "1500.75",
        "icon": "bank"
    }
    res = client.post("/accounts", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 201
    assert res.json["name"] == data["name"]
    assert res.json["type"] == data["type"]
    assert res.json["initial_balance"] == data["initial_balance"]
    assert res.json["icon"] == data["icon"]
    assert res.json["user_id"] == logged_in_user.id

    # Verify in DB
    account = Account.query.filter_by(user_id=logged_in_user.id).first()
    assert account is not None
    assert account.name == data["name"]
    assert account.initial_balance == Decimal(data["initial_balance"])

def test_add_account_missing_name(client, logged_in_user):
    """Test adding account with missing name."""
    data = {
        "type": "Poupança",
        "initial_balance": "100.00"
    }
    res = client.post("/accounts", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    assert "Invalid or missing 'name'" in res.json["error"]

def test_add_account_invalid_balance(client, logged_in_user):
    """Test adding account with invalid balance format."""
    data = {
        "name": "Investimentos",
        "type": "Investimento",
        "initial_balance": "abc"
    }
    res = client.post("/accounts", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    assert "Invalid 'initial_balance' format" in res.json["error"]

def test_list_accounts_populated(client, logged_in_user, init_database):
    """Test listing accounts when some exist."""
    # Add some accounts first
    acc1 = Account(user_id=logged_in_user.id, name="Conta A", type="Corrente", initial_balance=Decimal("100.00"))
    acc2 = Account(user_id=logged_in_user.id, name="Conta B", type="Poupança", initial_balance=Decimal("200.50"))
    db = init_database
    db.session.add_all([acc1, acc2])
    db.session.commit()

    res = client.get("/accounts")
    assert res.status_code == 200
    assert len(res.json) == 2
    # Check if names are present (order might vary based on DB/query)
    names = {item["name"] for item in res.json}
    assert "Conta A" in names
    assert "Conta B" in names

def test_get_account_success(client, logged_in_user, init_database):
    """Test getting a specific account successfully."""
    acc = Account(user_id=logged_in_user.id, name="Carteira", type="Dinheiro", initial_balance=Decimal("50.00"))
    db = init_database
    db.session.add(acc)
    db.session.commit()

    res = client.get(f"/accounts/{acc.id}")
    assert res.status_code == 200
    assert res.json["id"] == acc.id
    assert res.json["name"] == "Carteira"

def test_get_account_not_found(client, logged_in_user):
    """Test getting a non-existent account."""
    res = client.get("/accounts/999")
    assert res.status_code == 404
    assert "Account not found" in res.json["error"]

def test_get_account_unauthorized(client, logged_in_user, init_database):
    """Test getting an account belonging to another user."""
    # Create another user and their account
    other_user = User(username="otheruser", email="other@example.com")
    other_user.set_password("password")
    db = init_database
    db.session.add(other_user)
    db.session.commit()
    other_acc = Account(user_id=other_user.id, name="Other Account", type="Corrente", initial_balance=Decimal("1000.00"))
    db.session.add(other_acc)
    db.session.commit()

    res = client.get(f"/accounts/{other_acc.id}")
    assert res.status_code == 403
    assert "Unauthorized access" in res.json["error"]

def test_update_account_success(client, logged_in_user, init_database):
    """Test successfully updating an account."""
    acc = Account(user_id=logged_in_user.id, name="Old Name", type="Old Type", initial_balance=Decimal("10.00"))
    db = init_database
    db.session.add(acc)
    db.session.commit()

    update_data = {
        "name": "New Name",
        "type": "New Type",
        "initial_balance": "25.50",
        "icon": "updated-icon"
    }
    res = client.put(f"/accounts/{acc.id}", data=json.dumps(update_data), content_type="application/json")
    assert res.status_code == 200
    assert res.json["name"] == update_data["name"]
    assert res.json["type"] == update_data["type"]
    assert res.json["initial_balance"] == update_data["initial_balance"]
    assert res.json["icon"] == update_data["icon"]

    # Verify in DB
    updated_acc = Account.query.get(acc.id)
    assert updated_acc.name == update_data["name"]
    assert updated_acc.initial_balance == Decimal(update_data["initial_balance"])

def test_update_account_not_found(client, logged_in_user):
    """Test updating a non-existent account."""
    update_data = {"name": "Fail", "type": "Fail", "initial_balance": "0"}
    res = client.put("/accounts/999", data=json.dumps(update_data), content_type="application/json")
    assert res.status_code == 404

def test_update_account_unauthorized(client, logged_in_user, init_database):
    """Test updating an account belonging to another user."""
    other_user = User(username="otheruser2", email="other2@example.com")
    other_user.set_password("password")
    db = init_database
    db.session.add(other_user)
    db.session.commit()
    other_acc = Account(user_id=other_user.id, name="Untouchable", type="Corrente", initial_balance=Decimal("500.00"))
    db.session.add(other_acc)
    db.session.commit()

    update_data = {"name": "Hacked", "type": "Hacked", "initial_balance": "0"}
    res = client.put(f"/accounts/{other_acc.id}", data=json.dumps(update_data), content_type="application/json")
    assert res.status_code == 403

def test_delete_account_success(client, logged_in_user, init_database):
    """Test successfully deleting an account."""
    acc = Account(user_id=logged_in_user.id, name="To Delete", type="Temp", initial_balance=Decimal("1.00"))
    db = init_database
    db.session.add(acc)
    db.session.commit()
    account_id = acc.id

    res = client.delete(f"/accounts/{account_id}")
    assert res.status_code == 200
    assert "Account deleted successfully" in res.json["message"]

    # Verify in DB
    deleted_acc = Account.query.get(account_id)
    assert deleted_acc is None

def test_delete_account_not_found(client, logged_in_user):
    """Test deleting a non-existent account."""
    res = client.delete("/accounts/999")
    assert res.status_code == 404

def test_delete_account_unauthorized(client, logged_in_user, init_database):
    """Test deleting an account belonging to another user."""
    other_user = User(username="otheruser3", email="other3@example.com")
    other_user.set_password("password")
    db = init_database
    db.session.add(other_user)
    db.session.commit()
    other_acc = Account(user_id=other_user.id, name="Safe", type="Corrente", initial_balance=Decimal("999.00"))
    db.session.add(other_acc)
    db.session.commit()

    res = client.delete(f"/accounts/{other_acc.id}")
    assert res.status_code == 403

# TODO: Add test case for deleting account with transactions if that logic is implemented

