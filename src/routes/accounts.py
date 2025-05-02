# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from decimal import Decimal, InvalidOperation

from src.extensions import db
from src.models.account import Account

# Create the blueprint
accounts_bp = Blueprint("accounts", __name__)

# --- Helper Function ---
def account_to_dict(account):
    """Converts an Account object to a dictionary for JSON serialization."""
    return {
        "id": account.id,
        "user_id": account.user_id,
        "name": account.name,
        "type": account.type,
        "initial_balance": str(account.initial_balance), # Convert Decimal to string
        "icon": account.icon,
        "created_at": account.created_at.isoformat() # Use ISO format for datetime
    }

# --- Routes ---
@accounts_bp.route("/accounts", methods=["GET"])
@login_required
def list_accounts():
    """API endpoint to list all accounts for the current user."""
    try:
        user_accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.name).all()
        return jsonify([account_to_dict(acc) for acc in user_accounts]), 200
    except Exception as e:
        # Log the error e
        return jsonify({"error": "An unexpected error occurred"}), 500

@accounts_bp.route("/accounts/<int:account_id>", methods=["GET"])
@login_required
def get_account(account_id):
    """API endpoint to get a specific account by ID."""
    try:
        account = Account.query.get(account_id)
        if not account:
            return jsonify({"error": "Account not found"}), 404
        if account.user_id != current_user.id:
            return jsonify({"error": "Unauthorized access"}), 403
        return jsonify(account_to_dict(account)), 200
    except Exception as e:
        # Log the error e
        return jsonify({"error": "An unexpected error occurred"}), 500

@accounts_bp.route("/accounts", methods=["POST"])
@login_required
def add_account():
    """API endpoint to add a new account for the current user."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input, JSON required"}), 400

    name = data.get("name")
    account_type = data.get("type")
    initial_balance_str = data.get("initial_balance", "0.00")
    icon = data.get("icon")

    # Basic Validation
    if not name or not isinstance(name, str) or len(name) > 100:
        return jsonify({"error": "Invalid or missing 'name'"}), 400
    if not account_type or not isinstance(account_type, str) or len(account_type) > 50:
         # TODO: Validate against a predefined list of types?
        return jsonify({"error": "Invalid or missing 'type'"}), 400
    if icon and (not isinstance(icon, str) or len(icon) > 50):
        return jsonify({"error": "Invalid 'icon'"}), 400

    try:
        initial_balance = Decimal(initial_balance_str)
    except (InvalidOperation, TypeError):
        return jsonify({"error": "Invalid 'initial_balance' format"}), 400

    try:
        new_account = Account(
            user_id=current_user.id,
            name=name,
            type=account_type,
            initial_balance=initial_balance,
            icon=icon
        )
        db.session.add(new_account)
        db.session.commit()
        return jsonify(account_to_dict(new_account)), 201 # 201 Created status
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"error": "Failed to add account"}), 500

@accounts_bp.route("/accounts/<int:account_id>", methods=["PUT"])
@login_required
def update_account(account_id):
    """API endpoint to update an existing account (full update)."""
    account = Account.query.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    if account.user_id != current_user.id:
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input, JSON required"}), 400

    name = data.get("name")
    account_type = data.get("type")
    initial_balance_str = data.get("initial_balance")
    icon = data.get("icon")

    # Basic Validation (similar to POST, ensure all required fields for PUT are present)
    if not name or not isinstance(name, str) or len(name) > 100:
        return jsonify({"error": "Invalid or missing 'name'"}), 400
    if not account_type or not isinstance(account_type, str) or len(account_type) > 50:
        return jsonify({"error": "Invalid or missing 'type'"}), 400
    if initial_balance_str is None: # Required for PUT
        return jsonify({"error": "Missing 'initial_balance'"}), 400
    if icon and (not isinstance(icon, str) or len(icon) > 50):
        return jsonify({"error": "Invalid 'icon'"}), 400

    try:
        initial_balance = Decimal(initial_balance_str)
    except (InvalidOperation, TypeError):
        return jsonify({"error": "Invalid 'initial_balance' format"}), 400

    try:
        account.name = name
        account.type = account_type
        account.initial_balance = initial_balance
        account.icon = icon
        db.session.commit()
        return jsonify(account_to_dict(account)), 200
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"error": "Failed to update account"}), 500

@accounts_bp.route("/accounts/<int:account_id>", methods=["DELETE"])
@login_required
def delete_account(account_id):
    """API endpoint to delete an account."""
    account = Account.query.get(account_id)
    if not account:
        return jsonify({"error": "Account not found"}), 404
    if account.user_id != current_user.id:
        return jsonify({"error": "Unauthorized access"}), 403

    # Optional: Check for associated transactions before deleting
    # from src.models.transaction import Transaction # Import here or globally if needed
    # if Transaction.query.filter_by(account_id=account_id).first():
    #     return jsonify({"error": "Cannot delete account with associated transactions"}), 400

    try:
        db.session.delete(account)
        db.session.commit()
        return jsonify({"message": "Account deleted successfully"}), 200 # Or 204 No Content
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"error": "Failed to delete account"}), 500

# Remove form-based routes or comment them out if needed temporarily
# class AccountForm(FlaskForm): ...
# @accounts_bp.route("/accounts/add", methods=["GET", "POST"]) ...
# @accounts_bp.route("/accounts/edit/<int:account_id>", methods=["GET", "POST"]) ...
# @accounts_bp.route("/accounts/delete/<int:account_id>", methods=["POST"]) ...

