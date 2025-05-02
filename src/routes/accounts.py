# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from wtforms import StringField, SelectField, DecimalField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Optional

from src.extensions import db
from src.models.account import Account

# Create the blueprint
accounts_bp = Blueprint("accounts", __name__, template_folder="../templates")

# --- Forms ---
class AccountForm(FlaskForm):
    name = StringField("Nome da Conta", validators=[DataRequired(), Length(max=100)])
    # Choices should ideally be dynamic or defined constants
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
    submit = SubmitField("Salvar Conta")

# --- Routes ---
@accounts_bp.route("/accounts")
@login_required
def list_accounts():
    """List all accounts for the current user."""
    user_accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.name).all()
    return render_template("accounts_list.html", accounts=user_accounts, title="Minhas Contas")

@accounts_bp.route("/accounts/add", methods=["GET", "POST"])
@login_required
def add_account():
    """Add a new account for the current user."""
    form = AccountForm()
    if form.validate_on_submit():
        new_account = Account(
            user_id=current_user.id,
            name=form.name.data,
            type=form.type.data,
            initial_balance=form.initial_balance.data,
            icon=form.icon.data
        )
        db.session.add(new_account)
        db.session.commit()
        flash("Conta adicionada com sucesso!")
        return redirect(url_for("accounts.list_accounts")) # Redirect to list view for now
    # Render a template with the form (to be created)
    # return render_template("add_account.html", title="Adicionar Conta", form=form)
    # Temporary response
    return jsonify({"message": "GET request to add_account. Use POST to submit form."})

@accounts_bp.route("/accounts/edit/<int:account_id>", methods=["GET", "POST"])
@login_required
def edit_account(account_id):
    """Edit an existing account."""
    account = Account.query.get_or_404(account_id)
    # Ensure the user owns this account
    if account.user_id != current_user.id:
        flash("Acesso não autorizado.")
        return redirect(url_for("accounts.list_accounts"))

    form = AccountForm(obj=account) # Pre-populate form
    if form.validate_on_submit():
        account.name = form.name.data
        account.type = form.type.data
        account.initial_balance = form.initial_balance.data
        account.icon = form.icon.data
        db.session.commit()
        flash("Conta atualizada com sucesso!")
        return redirect(url_for("accounts.list_accounts"))
    # Render a template with the form (to be created)
    # return render_template("edit_account.html", title="Editar Conta", form=form, account_id=account_id)
    # Temporary response
    return jsonify({"message": f"GET request to edit_account {account_id}. Use POST to submit form."})

@accounts_bp.route("/accounts/delete/<int:account_id>", methods=["POST"]) # Use POST for deletion
@login_required
def delete_account(account_id):
    """Delete an account."""
    account = Account.query.get_or_404(account_id)
    # Ensure the user owns this account
    if account.user_id != current_user.id:
        flash("Acesso não autorizado.")
        return redirect(url_for("accounts.list_accounts"))

    # Check for associated transactions before deleting (optional, depends on desired behavior)
    # if account.transactions.count() > 0:
    #     flash("Não é possível excluir contas com transações associadas.")
    #     return redirect(url_for("accounts.list_accounts"))

    db.session.delete(account)
    db.session.commit()
    flash("Conta excluída com sucesso!")
    return redirect(url_for("accounts.list_accounts"))

