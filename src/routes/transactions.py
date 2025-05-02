# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from wtforms import StringField, SelectField, DecimalField, DateField, BooleanField, SubmitField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Optional
from datetime import date

from src.extensions import db
from src.models.transaction import Transaction
from src.models.account import Account
from src.models.category import Category

# Create the blueprint
transactions_bp = Blueprint("transactions", __name__, template_folder="../static")

# --- Helper Functions for Form Choices ---
def get_user_accounts():
    """Returns a query for the current user\s accounts."""
    return Account.query.filter_by(user_id=current_user.id).order_by(Account.name)

def get_user_categories(transaction_type):
    """Returns a query for the current user\s categories based on type."""
    return Category.query.filter(
        ((Category.user_id == current_user.id) | (Category.is_default == True)),
        Category.type == transaction_type
    ).order_by(Category.name)

# --- Forms ---
class TransactionForm(FlaskForm):
    type = SelectField("Tipo", choices=[("Despesa", "Despesa"), ("Receita", "Receita")], validators=[DataRequired()])
    description = StringField("Descrição", validators=[Optional(), Length(max=200)])
    amount = DecimalField("Valor", validators=[DataRequired()], places=2)
    date = DateField("Data", format="%Y-%m-%d", default=date.today, validators=[DataRequired()])
    # Use QuerySelectField to dynamically load accounts and categories
    account = QuerySelectField("Conta", query_factory=get_user_accounts, get_label="name", allow_blank=False, validators=[DataRequired()])
    # Category choices depend on the selected type (handled dynamically or in the view)
    category = QuerySelectField("Categoria", query_factory=lambda: get_user_categories("Despesa"), get_label="name", allow_blank=False, validators=[DataRequired()]) # Default to Despesa
    is_paid = BooleanField("Pago", default=True) # Relevant for Despesa
    is_received = BooleanField("Recebido", default=True) # Relevant for Receita
    # attachment_url = StringField("Anexo URL", validators=[Optional(), Length(max=255)]) # Add later if needed
    submit = SubmitField("Salvar Transação")

# --- Routes ---
@transactions_bp.route("/transactions")
@login_required
def list_transactions():
    """List all transactions for the current user (potentially with filters)."""
    # Add filtering based on request args later (period, account, category, type)
    user_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()

    # For now, returning JSON, will integrate with template later
    return jsonify([{
        "id": t.id,
        "date": t.date.isoformat(),
        "description": t.description,
        "amount": str(t.amount),
        "type": t.type,
        "account": t.account.name,
        "category": t.category.name
    } for t in user_transactions])

# Route to dynamically get categories based on type for the form
@transactions_bp.route("/_get_categories/<transaction_type>")
@login_required
def _get_categories(transaction_type):
    categories = get_user_categories(transaction_type).all()
    return jsonify([{"id": cat.id, "name": cat.name} for cat in categories])

@transactions_bp.route("/transactions/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    """Add a new transaction for the current user."""
    form = TransactionForm()
    # Dynamically set category choices based on initial/POSTed type
    form.category.query_factory = lambda: get_user_categories(form.type.data or "Despesa")

    if form.validate_on_submit():
        new_transaction = Transaction(
            user_id=current_user.id,
            account_id=form.account.data.id,
            category_id=form.category.data.id,
            description=form.description.data,
            amount=form.amount.data,
            type=form.type.data,
            date=form.date.data,
            # Set paid/received based on type
            is_paid=form.is_paid.data if form.type.data == "Despesa" else True,
            is_received=form.is_received.data if form.type.data == "Receita" else True
        )
        db.session.add(new_transaction)
        db.session.commit()
        flash("Transação adicionada com sucesso!")
        return redirect(url_for("transactions.list_transactions")) # Redirect to list view

    # Render a template with the form (to be created)
    # return render_template("add_transaction.html", title="Adicionar Transação", form=form)
    # Temporary response
    return jsonify({"message": "GET request to add_transaction. Use POST to submit form."})

@transactions_bp.route("/transactions/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    """Edit an existing transaction."""
    transaction = Transaction.query.get_or_404(transaction_id)
    # Ensure the user owns this transaction
    if transaction.user_id != current_user.id:
        flash("Acesso não autorizado.")
        return redirect(url_for("transactions.list_transactions"))

    form = TransactionForm(obj=transaction)
    # Dynamically set category choices based on initial/POSTed type
    form.category.query_factory = lambda: get_user_categories(form.type.data or transaction.type)

    if form.validate_on_submit():
        transaction.account_id = form.account.data.id
        transaction.category_id = form.category.data.id
        transaction.description = form.description.data
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.date = form.date.data
        transaction.is_paid = form.is_paid.data if form.type.data == "Despesa" else True
        transaction.is_received = form.is_received.data if form.type.data == "Receita" else True
        db.session.commit()
        flash("Transação atualizada com sucesso!")
        return redirect(url_for("transactions.list_transactions"))

    # Render a template with the form (to be created)
    # return render_template("edit_transaction.html", title="Editar Transação", form=form, transaction_id=transaction_id)
    # Temporary response
    return jsonify({"message": f"GET request to edit_transaction {transaction_id}. Use POST to submit form."})

@transactions_bp.route("/transactions/delete/<int:transaction_id>", methods=["POST"]) # Use POST for deletion
@login_required
def delete_transaction(transaction_id):
    """Delete a transaction."""
    transaction = Transaction.query.get_or_404(transaction_id)
    # Ensure the user owns this transaction
    if transaction.user_id != current_user.id:
        flash("Acesso não autorizado.")
        return redirect(url_for("transactions.list_transactions"))

    db.session.delete(transaction)
    db.session.commit()
    flash("Transação excluída com sucesso!")
    return redirect(url_for("transactions.list_transactions"))

