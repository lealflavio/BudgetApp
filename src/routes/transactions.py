# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from wtforms import StringField, SelectField, DecimalField, DateField, BooleanField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from datetime import date
from decimal import Decimal
from typing import List, Dict, Any

from src.extensions import db
from src.models.transaction import Transaction, TRANSACTION_TYPE_DESPESA, TRANSACTION_TYPE_RECEITA
from src.models.account import Account
from src.models.category import Category

# Create the blueprint
transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions", template_folder="../templates") # Added url_prefix and corrected template_folder

# --- Helper Functions for Form Choices ---
def get_user_accounts():
    """Returns a query for the current user's accounts."""
    return Account.query.filter_by(user_id=current_user.id).order_by(Account.name)

def get_user_categories(transaction_type: str):
    """Returns a query for the current user's categories based on type."""
    # Ensure valid type
    if transaction_type not in [TRANSACTION_TYPE_DESPESA, TRANSACTION_TYPE_RECEITA]:
        transaction_type = TRANSACTION_TYPE_DESPESA # Default to Despesa if invalid

    return Category.query.filter(
        ((Category.user_id == current_user.id) | (Category.is_default == True)),
        Category.type == transaction_type
    ).order_by(Category.name)

# --- Forms ---
class TransactionForm(FlaskForm):
    type = SelectField(
        "Tipo",
        choices=[(TRANSACTION_TYPE_DESPESA, "Despesa"), (TRANSACTION_TYPE_RECEITA, "Receita")],
        validators=[DataRequired()]
    )
    description = StringField("Descrição", validators=[Optional(), Length(max=200)])
    amount = DecimalField("Valor", validators=[DataRequired()], places=2)
    date = DateField("Data", format="%Y-%m-%d", default=date.today, validators=[DataRequired()])
    account = QuerySelectField(
        "Conta",
        query_factory=get_user_accounts,
        get_label="name",
        allow_blank=False,
        validators=[DataRequired()]
    )
    # Category choices depend on the selected type (handled dynamically in the view/JS)
    category = QuerySelectField(
        "Categoria",
        # Provide a default query factory, will be updated dynamically
        query_factory=lambda: get_user_categories(TRANSACTION_TYPE_DESPESA),
        get_label="name",
        allow_blank=False,
        validators=[DataRequired()]
    )
    is_paid = BooleanField("Pago", default=True) # Relevant for Despesa
    is_received = BooleanField("Recebido", default=True) # Relevant for Receita
    # attachment_url = StringField("Anexo URL", validators=[Optional(), Length(max=255)]) # Add later if needed
    submit = SubmitField("Salvar Transação")

    def validate_amount(self, field):
        if field.data is not None and field.data <= 0:
            raise ValidationError("O valor deve ser positivo.")

# --- API Routes (returning JSON) ---
@transactions_bp.route("/api", methods=["GET"])
@login_required
def api_list_transactions():
    """API endpoint to list all transactions for the current user (JSON)."""
    # TODO: Add filtering based on request args (period, account, category, type)
    try:
        user_transactions: List[Transaction] = Transaction.query.filter_by(
            user_id=current_user.id
        ).order_by(Transaction.date.desc()).all()

        return jsonify([t.to_dict() for t in user_transactions])
    except Exception as e:
        # Log the error e
        return jsonify({"error": "Erro ao buscar transações"}), 500

@transactions_bp.route("/api/<int:transaction_id>", methods=["GET"])
@login_required
def api_get_transaction(transaction_id: int):
    """API endpoint to get a single transaction by ID (JSON)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction is None:
        return jsonify({"error": "Transação não encontrada ou não autorizada"}), 404
    return jsonify(transaction.to_dict())

@transactions_bp.route("/api", methods=["POST"])
@login_required
def api_add_transaction():
    """API endpoint to add a new transaction (JSON)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição inválida, JSON esperado"}), 400

    # Basic validation (more robust validation needed)
    required_fields = ["type", "amount", "date", "account_id", "category_id"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Campos obrigatórios ausentes: {required_fields}"}), 400

    try:
        amount = Decimal(data["amount"])
        if amount <= 0:
             return jsonify({"error": "O valor deve ser positivo"}), 400

        # Validate account and category belong to user or are default
        account = Account.query.filter_by(id=data["account_id"], user_id=current_user.id).first()
        category = Category.query.filter(
            Category.id == data["category_id"],
            ((Category.user_id == current_user.id) | (Category.is_default == True))
        ).first()

        if not account:
            return jsonify({"error": "Conta inválida ou não pertence ao usuário"}), 400
        if not category:
            return jsonify({"error": "Categoria inválida ou não pertence ao usuário"}), 400
        if category.type != data["type"]:
             return jsonify({"error": f"Tipo da categoria ({category.type}) não corresponde ao tipo da transação ({data['type']})"}), 400

        new_transaction = Transaction(
            user_id=current_user.id,
            account_id=data["account_id"],
            category_id=data["category_id"],
            description=data.get("description"),
            amount=amount,
            type=data["type"],
            date=date.fromisoformat(data["date"]),
            is_paid=data.get("is_paid", True) if data["type"] == TRANSACTION_TYPE_DESPESA else True,
            is_received=data.get("is_received", True) if data["type"] == TRANSACTION_TYPE_RECEITA else True
            # attachment_url=data.get("attachment_url") # Add later
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify(new_transaction.to_dict()), 201 # Return created object and 201 status
    except (ValueError, TypeError) as e:
         # Log error e
         return jsonify({"error": f"Erro nos dados fornecidos: {e}"}), 400
    except Exception as e:
        # Log error e
        db.session.rollback()
        return jsonify({"error": "Erro interno ao salvar transação"}), 500

@transactions_bp.route("/api/<int:transaction_id>", methods=["PUT", "PATCH"])
@login_required
def api_edit_transaction(transaction_id: int):
    """API endpoint to edit an existing transaction (JSON)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction is None:
        return jsonify({"error": "Transação não encontrada ou não autorizada"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição inválida, JSON esperado"}), 400

    try:
        # Update fields present in the request data
        if "account_id" in data:
            account = Account.query.filter_by(id=data["account_id"], user_id=current_user.id).first()
            if not account: return jsonify({"error": "Conta inválida ou não pertence ao usuário"}), 400
            transaction.account_id = data["account_id"]

        if "category_id" in data:
            category = Category.query.filter(
                Category.id == data["category_id"],
                ((Category.user_id == current_user.id) | (Category.is_default == True))
            ).first()
            if not category: return jsonify({"error": "Categoria inválida ou não pertence ao usuário"}), 400
            # Ensure category type matches transaction type if type is not being changed simultaneously
            current_type = data.get("type", transaction.type)
            if category.type != current_type:
                 return jsonify({"error": f"Tipo da categoria ({category.type}) não corresponde ao tipo da transação ({current_type})"}), 400
            transaction.category_id = data["category_id"]

        if "description" in data:
            transaction.description = data["description"]
        if "amount" in data:
            amount = Decimal(data["amount"])
            if amount <= 0: return jsonify({"error": "O valor deve ser positivo"}), 400
            transaction.amount = amount
        if "type" in data:
            # If type changes, re-validate category
            if "category_id" in data and category.type != data["type"]:
                 return jsonify({"error": f"Tipo da categoria ({category.type}) não corresponde ao novo tipo da transação ({data['type']})"}), 400
            elif "category_id" not in data and transaction.category.type != data["type"]:
                 return jsonify({"error": f"Tipo da categoria existente ({transaction.category.type}) não corresponde ao novo tipo da transação ({data['type']}). Altere a categoria também."}) , 400
            transaction.type = data["type"]
        if "date" in data:
            transaction.date = date.fromisoformat(data["date"])
        if "is_paid" in data and transaction.type == TRANSACTION_TYPE_DESPESA:
            transaction.is_paid = data["is_paid"]
        if "is_received" in data and transaction.type == TRANSACTION_TYPE_RECEITA:
            transaction.is_received = data["is_received"]
        # if "attachment_url" in data: transaction.attachment_url = data["attachment_url"]

        db.session.commit()
        return jsonify(transaction.to_dict())
    except (ValueError, TypeError) as e:
         # Log error e
         return jsonify({"error": f"Erro nos dados fornecidos: {e}"}), 400
    except Exception as e:
        # Log error e
        db.session.rollback()
        return jsonify({"error": "Erro interno ao atualizar transação"}), 500

@transactions_bp.route("/api/<int:transaction_id>", methods=["DELETE"])
@login_required
def api_delete_transaction(transaction_id: int):
    """API endpoint to delete a transaction (JSON)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction is None:
        return jsonify({"error": "Transação não encontrada ou não autorizada"}), 404

    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transação excluída com sucesso"}), 200 # Use 200 or 204
    except Exception as e:
        # Log error e
        db.session.rollback()
        return jsonify({"error": "Erro interno ao excluir transação"}), 500

# --- Route for dynamic form category choices (used by frontend JS) ---
@transactions_bp.route("/_get_categories/<transaction_type>")
@login_required
def _get_categories(transaction_type: str):
    """Returns categories for the form based on transaction type."""
    categories = get_user_categories(transaction_type).all()
    return jsonify([{"id": cat.id, "name": cat.name} for cat in categories])


# --- HTML Routes (Using Forms - To be used by Frontend Agents) ---
# Note: These routes might be replaced or adapted by frontend agents using the API routes above.

@transactions_bp.route("/") # Changed from /transactions to / within the blueprint
@login_required
def list_transactions_view():
    """View to list all transactions for the current user (HTML)."""
    # This view will likely use JavaScript to call the /api endpoint
    return render_template("transactions/list.html", title="Transações")

@transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction_view():
    """View to add a new transaction for the current user (HTML Form)."""
    form = TransactionForm()
    # Dynamically set category choices based on initial/POSTed type
    # This needs JS on the frontend to call /_get_categories/<type>
    form.category.query_factory = lambda: get_user_categories(form.type.data or TRANSACTION_TYPE_DESPESA)

    if form.validate_on_submit():
        try:
            # Re-validate category type against transaction type
            category = Category.query.get(form.category.data.id)
            if not category or category.type != form.type.data:
                flash(f"Tipo da categoria ({category.type if category else 'N/A'}) não corresponde ao tipo da transação ({form.type.data}).", "danger")
                # Need to re-render form with error, potentially repopulating dynamic fields
                return render_template("transactions/add_edit.html", title="Adicionar Transação", form=form, action_url=url_for('transactions.add_transaction_view'))

            new_transaction = Transaction(
                user_id=current_user.id,
                account_id=form.account.data.id,
                category_id=form.category.data.id,
                description=form.description.data,
                amount=form.amount.data,
                type=form.type.data,
                date=form.date.data,
                is_paid=form.is_paid.data if form.type.data == TRANSACTION_TYPE_DESPESA else True,
                is_received=form.is_received.data if form.type.data == TRANSACTION_TYPE_RECEITA else True
            )
            db.session.add(new_transaction)
            db.session.commit()
            flash("Transação adicionada com sucesso!", "success")
            return redirect(url_for("transactions.list_transactions_view"))
        except Exception as e:
            # Log error e
            db.session.rollback()
            flash("Erro ao salvar a transação.", "danger")

    # Render the template with the form
    return render_template("transactions/add_edit.html", title="Adicionar Transação", form=form, action_url=url_for('transactions.add_transaction_view'))

@transactions_bp.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction_view(transaction_id: int):
    """View to edit an existing transaction (HTML Form)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()

    form = TransactionForm(obj=transaction)
    # Dynamically set category choices based on initial/POSTed type
    # This needs JS on the frontend to call /_get_categories/<type>
    form.category.query_factory = lambda: get_user_categories(form.type.data or transaction.type)

    if form.validate_on_submit():
        try:
            # Re-validate category type against transaction type
            category = Category.query.get(form.category.data.id)
            if not category or category.type != form.type.data:
                flash(f"Tipo da categoria ({category.type if category else 'N/A'}) não corresponde ao tipo da transação ({form.type.data}).", "danger")
                return render_template("transactions/add_edit.html", title="Editar Transação", form=form, transaction_id=transaction_id, action_url=url_for('transactions.edit_transaction_view', transaction_id=transaction_id))

            transaction.account_id = form.account.data.id
            transaction.category_id = form.category.data.id
            transaction.description = form.description.data
            transaction.amount = form.amount.data
            transaction.type = form.type.data
            transaction.date = form.date.data
            transaction.is_paid = form.is_paid.data if form.type.data == TRANSACTION_TYPE_DESPESA else True
            transaction.is_received = form.is_received.data if form.type.data == TRANSACTION_TYPE_RECEITA else True
            db.session.commit()
            flash("Transação atualizada com sucesso!", "success")
            return redirect(url_for("transactions.list_transactions_view"))
        except Exception as e:
            # Log error e
            db.session.rollback()
            flash("Erro ao atualizar a transação.", "danger")

    # Render the template with the form
    return render_template("transactions/add_edit.html", title="Editar Transação", form=form, transaction_id=transaction_id, action_url=url_for('transactions.edit_transaction_view', transaction_id=transaction_id))

@transactions_bp.route("/delete/<int:transaction_id>", methods=["POST"]) # Use POST for deletion in HTML forms too
@login_required
def delete_transaction_view(transaction_id: int):
    """Action to delete a transaction (called from HTML form/button)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction is None:
        flash("Transação não encontrada ou não autorizada.", "warning")
        return redirect(url_for("transactions.list_transactions_view"))

    try:
        db.session.delete(transaction)
        db.session.commit()
        flash("Transação excluída com sucesso!", "success")
    except Exception as e:
        # Log error e
        db.session.rollback()
        flash("Erro ao excluir a transação.", "danger")

    return redirect(url_for("transactions.list_transactions_view"))

