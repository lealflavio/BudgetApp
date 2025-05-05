# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from wtforms import StringField, SelectField, DecimalField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Optional

from src.extensions import db
from src.models.account import Account

# Create the blueprint
accounts_bp = Blueprint("accounts", __name__, template_folder="../static")

# --- Forms ---
class AccountForm(FlaskForm):
    name = StringField("Nome da Conta", validators=[DataRequired(), Length(max=100)])
    type = SelectField("Tipo", choices=[
        ("Conta Corrente", "Conta Corrente"),
        ("Poupança", "Poupança"),
        ("Cartão de Crédito", "Cartão de Crédito"),
        ("Dinheiro", "Dinheiro"),
        ("Investimento", "Investimento"),
        ("Outro", "Outro")
    ], validators=[DataRequired()])
    initial_balance = DecimalField("Saldo Inicial", default=0.00, validators=[Optional()])
    icon = StringField("Ícone (Opcional)", validators=[Optional(), Length(max=50)])
    submit = SubmitField("Salvar Conta") # Keep for template rendering, not used by API

# --- API Routes ---
@accounts_bp.route("/accounts", methods=["GET"])
@login_required
def list_accounts_api():
    """API endpoint to list all accounts for the current user (JSON)."""
    user_accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.name).all()
    return jsonify([{
        "id": acc.id,
        "name": acc.name,
        "type": acc.type,
        "initial_balance": str(acc.initial_balance) # Convert Decimal to string for JSON
    } for acc in user_accounts])

@accounts_bp.route("/accounts/add", methods=["POST"])
@login_required
def add_account_api():
    """API endpoint to add a new account (handles JSON request)."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Requisição inválida. JSON esperado."}), 400

    # Use data=data for WTForms >= 3.0, might need formdata=None for older versions
    form = AccountForm(data=data, meta={\"csrf\": False}) # Disable CSRF for API endpoint if token is in header

    if form.validate():
        try:
            new_account = Account(
                user_id=current_user.id,
                name=form.name.data,
                type=form.type.data,
                initial_balance=form.initial_balance.data if form.initial_balance.data is not None else 0.00,
                icon=form.icon.data
            )
            db.session.add(new_account)
            db.session.commit()
            return jsonify({"success": True, "message": "Conta adicionada com sucesso!", "account_id": new_account.id}), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error adding account: {e}") # Log the error
            return jsonify({"success": False, "message": "Erro interno ao adicionar conta."}), 500
    else:
        return jsonify({"success": False, "message": "Dados inválidos.", "errors": form.errors}), 400

@accounts_bp.route("/accounts/edit/<int:account_id>", methods=["PUT"])
@login_required
def edit_account_api(account_id):
    """API endpoint to edit an existing account (handles JSON request)."""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({"success": False, "message": "Conta não encontrada ou não autorizada."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Requisição inválida. JSON esperado."}), 400

    form = AccountForm(data=data, meta={\"csrf\": False})

    if form.validate():
        try:
            account.name = form.name.data
            account.type = form.type.data
            account.initial_balance = form.initial_balance.data if form.initial_balance.data is not None else account.initial_balance
            account.icon = form.icon.data
            db.session.commit()
            return jsonify({"success": True, "message": "Conta atualizada com sucesso!"}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error updating account: {e}") # Log the error
            return jsonify({"success": False, "message": "Erro interno ao atualizar conta."}), 500
    else:
        return jsonify({"success": False, "message": "Dados inválidos.", "errors": form.errors}), 400

@accounts_bp.route("/accounts/delete/<int:account_id>", methods=["DELETE"])
@login_required
def delete_account_api(account_id):
    """API endpoint to delete an account."""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({"success": False, "message": "Conta não encontrada ou não autorizada."}), 404

    try:
        # Optional: Check for dependencies like transactions before deleting
        # if account.transactions.count() > 0:
        #     return jsonify({"success": False, "message": "Não é possível excluir contas com transações associadas."}), 400

        db.session.delete(account)
        db.session.commit()
        return jsonify({"success": True, "message": "Conta excluída com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting account: {e}") # Log the error
        return jsonify({"success": False, "message": "Erro interno ao excluir conta."}), 500

# --- Page Rendering Routes ---
@accounts_bp.route("/accounts/list/page")
@login_required
def list_accounts_page():
    """Renders the page that lists accounts (data fetched via JS)."""
    return render_template("accounts_list.html", title="Minhas Contas")

@accounts_bp.route("/accounts/add/page", methods=["GET"])
@login_required
def add_account_page():
    """Renders the page with the form to add a new account."""
    form = AccountForm()
    return render_template("account_form.html", title="Adicionar Conta", form=form, account_id=None)

@accounts_bp.route("/accounts/edit/<int:account_id>/page", methods=["GET"])
@login_required
def edit_account_page(account_id):
    """Renders the page with the form to edit an existing account."""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    form = AccountForm(obj=account) # Pre-populate form with account data
    return render_template("account_form.html", title="Editar Conta", form=form, account_id=account_id)


