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
transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions") # Removed template_folder, focusing on API

# --- Helper Functions (Potentially move to a service/utils module later) ---
def get_user_accounts_query():
    """Returns a query for the current user's accounts."""
    return Account.query.filter_by(user_id=current_user.id).order_by(Account.name)

def get_user_categories_query(transaction_type: str):
    """Returns a query for the current user's categories based on type."""
    # Ensure valid type
    if transaction_type not in [TRANSACTION_TYPE_DESPESA, TRANSACTION_TYPE_RECEITA]:
        transaction_type = TRANSACTION_TYPE_DESPESA # Default to Despesa if invalid

    return Category.query.filter(
        ((Category.user_id == current_user.id) | (Category.is_default == True)),
        Category.type == transaction_type
    ).order_by(Category.name)

# --- Forms (Kept for potential future use or admin interface, but API is primary) ---
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
        query_factory=get_user_accounts_query,
        get_label="name",
        allow_blank=False,
        validators=[DataRequired()]
    )
    category = QuerySelectField(
        "Categoria",
        query_factory=lambda: get_user_categories_query(TRANSACTION_TYPE_DESPESA),
        get_label="name",
        allow_blank=False,
        validators=[DataRequired()]
    )
    is_paid = BooleanField("Pago", default=True)
    is_received = BooleanField("Recebido", default=True)
    submit = SubmitField("Salvar Transação")

    def validate_amount(self, field):
        if field.data is not None and field.data <= 0:
            raise ValidationError("O valor deve ser positivo.")

# --- API Routes (Primary Interface) ---
@transactions_bp.route("/api", methods=["GET"])
@login_required
def api_list_transactions():
    """API: List transactions for the current user (JSON). Supports filtering."""
    try:
        query = Transaction.query.filter_by(user_id=current_user.id)

        # Filtering (Example: add more filters as needed)
        account_id = request.args.get("account_id", type=int)
        category_id = request.args.get("category_id", type=int)
        trans_type = request.args.get("type")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if trans_type in [TRANSACTION_TYPE_DESPESA, TRANSACTION_TYPE_RECEITA]:
            query = query.filter(Transaction.type == trans_type)
        if start_date_str:
            try:
                start_date = date.fromisoformat(start_date_str)
                query = query.filter(Transaction.date >= start_date)
            except ValueError:
                return jsonify({"error": "Formato de data inicial inválido (YYYY-MM-DD)"}), 400
        if end_date_str:
            try:
                end_date = date.fromisoformat(end_date_str)
                query = query.filter(Transaction.date <= end_date)
            except ValueError:
                return jsonify({"error": "Formato de data final inválido (YYYY-MM-DD)"}), 400

        user_transactions: List[Transaction] = query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
        return jsonify([t.to_dict() for t in user_transactions])
    except Exception as e:
        # TODO: Log the error e
        print(f"Error fetching transactions: {e}") # Basic logging
        return jsonify({"error": "Erro ao buscar transações"}), 500

@transactions_bp.route("/api/<int:transaction_id>", methods=["GET"])
@login_required
def api_get_transaction(transaction_id: int):
    """API: Get a single transaction by ID (JSON)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction is None:
        return jsonify({"error": "Transação não encontrada ou não autorizada"}), 404
    return jsonify(transaction.to_dict())

@transactions_bp.route("/api", methods=["POST"])
@login_required
def api_add_transaction():
    """API: Add a new transaction (JSON)."""
    data: Dict[str, Any] | None = request.get_json()
    if not data:
        return jsonify({"error": "Requisição inválida, JSON esperado"}), 400

    required_fields = ["type", "amount", "date", "account_id", "category_id"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Campos obrigatórios ausentes: {', '.join(missing_fields)}"}), 400

    try:
        amount = Decimal(data["amount"])
        if amount <= 0:
             return jsonify({"error": "O valor deve ser positivo"}), 400

        trans_date = date.fromisoformat(data["date"])
        trans_type = data["type"]
        account_id = int(data["account_id"])
        category_id = int(data["category_id"])

        # Validate account and category belong to user or are default
        account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
        category = Category.query.filter(
            Category.id == category_id,
            ((Category.user_id == current_user.id) | (Category.is_default == True))
        ).first()

        if not account:
            return jsonify({"error": "Conta inválida ou não pertence ao usuário"}), 400
        if not category:
            return jsonify({"error": "Categoria inválida ou não pertence ao usuário"}), 400
        if category.type != trans_type:
             return jsonify({"error": f"Tipo da categoria ({category.type}) não corresponde ao tipo da transação ({trans_type})"}), 400

        new_transaction = Transaction(
            user_id=current_user.id,
            account_id=account_id,
            category_id=category_id,
            description=data.get("description"),
            amount=amount,
            type=trans_type,
            date=trans_date,
            # Set is_paid/is_received based on type, default to True if not provided
            is_paid=data.get("is_paid", True) if trans_type == TRANSACTION_TYPE_DESPESA else True,
            is_received=data.get("is_received", True) if trans_type == TRANSACTION_TYPE_RECEITA else True
        )
        # new_transaction.validate() # Use model validation if implemented
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify(new_transaction.to_dict()), 201 # Return created object and 201 status

    except (ValueError, TypeError) as e:
         # TODO: Log error e
         print(f"Data error adding transaction: {e}")
         return jsonify({"error": f"Erro nos dados fornecidos: {e}"}), 400
    except Exception as e:
        # TODO: Log error e
        print(f"Internal error adding transaction: {e}")
        db.session.rollback()
        return jsonify({"error": "Erro interno ao salvar transação"}), 500

@transactions_bp.route("/api/<int:transaction_id>", methods=["PUT", "PATCH"])
@login_required
def api_edit_transaction(transaction_id: int):
    """API: Edit an existing transaction (JSON). Supports partial updates (PATCH)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction is None:
        return jsonify({"error": "Transação não encontrada ou não autorizada"}), 404

    data: Dict[str, Any] | None = request.get_json()
    if not data:
        return jsonify({"error": "Requisição inválida, JSON esperado"}), 400

    try:
        updated = False
        # Update fields present in the request data
        if "account_id" in data:
            account_id = int(data["account_id"])
            account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
            if not account: return jsonify({"error": "Conta inválida ou não pertence ao usuário"}), 400
            if transaction.account_id != account_id:
                transaction.account_id = account_id
                updated = True

        if "category_id" in data:
            category_id = int(data["category_id"])
            category = Category.query.filter(
                Category.id == category_id,
                ((Category.user_id == current_user.id) | (Category.is_default == True))
            ).first()
            if not category: return jsonify({"error": "Categoria inválida ou não pertence ao usuário"}), 400
            # Ensure category type matches transaction type if type is not being changed simultaneously
            current_type = data.get("type", transaction.type)
            if category.type != current_type:
                 return jsonify({"error": f"Tipo da categoria ({category.type}) não corresponde ao tipo da transação ({current_type})"}), 400
            if transaction.category_id != category_id:
                transaction.category_id = category_id
                updated = True

        if "description" in data and transaction.description != data["description"]:
            transaction.description = data["description"]
            updated = True
        if "amount" in data:
            amount = Decimal(data["amount"])
            if amount <= 0: return jsonify({"error": "O valor deve ser positivo"}), 400
            if transaction.amount != amount:
                transaction.amount = amount
                updated = True
        if "type" in data and transaction.type != data["type"]:
            new_type = data["type"]
            if new_type not in [TRANSACTION_TYPE_DESPESA, TRANSACTION_TYPE_RECEITA]:
                return jsonify({"error": f"Tipo de transação inválido: {new_type}"}), 400
            # Re-validate category if type changes
            category_to_check = Category.query.get(transaction.category_id)
            if category_to_check and category_to_check.type != new_type:
                 # If category_id is also changing in the same request, it's handled above
                 if "category_id" not in data:
                     return jsonify({"error": f"Tipo da categoria existente ({category_to_check.type}) não corresponde ao novo tipo da transação ({new_type}). Altere a categoria também."}) , 400
            transaction.type = new_type
            updated = True
        if "date" in data:
            trans_date = date.fromisoformat(data["date"])
            if transaction.date != trans_date:
                transaction.date = trans_date
                updated = True
        if "is_paid" in data and transaction.type == TRANSACTION_TYPE_DESPESA and transaction.is_paid != data["is_paid"]:
            transaction.is_paid = data["is_paid"]
            updated = True
        if "is_received" in data and transaction.type == TRANSACTION_TYPE_RECEITA and transaction.is_received != data["is_received"]:
            transaction.is_received = data["is_received"]
            updated = True

        if updated:
            # transaction.validate() # Use model validation if implemented
            db.session.commit()
        return jsonify(transaction.to_dict())

    except (ValueError, TypeError) as e:
         # TODO: Log error e
         print(f"Data error editing transaction: {e}")
         return jsonify({"error": f"Erro nos dados fornecidos: {e}"}), 400
    except Exception as e:
        # TODO: Log error e
        print(f"Internal error editing transaction: {e}")
        db.session.rollback()
        return jsonify({"error": "Erro interno ao atualizar transação"}), 500

@transactions_bp.route("/api/<int:transaction_id>", methods=["DELETE"])
@login_required
def api_delete_transaction(transaction_id: int):
    """API: Delete a transaction (JSON)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction is None:
        return jsonify({"error": "Transação não encontrada ou não autorizada"}), 404

    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transação excluída com sucesso"}), 200 # Use 200 or 204 No Content
    except Exception as e:
        # TODO: Log error e
        print(f"Internal error deleting transaction: {e}")
        db.session.rollback()
        return jsonify({"error": "Erro interno ao excluir transação"}), 500

# --- Route for dynamic form category choices (Used by frontend JS if forms are used) ---
@transactions_bp.route("/_get_categories/<transaction_type>")
@login_required
def _get_categories(transaction_type: str):
    """Returns categories for the form based on transaction type (JSON)."""
    try:
        categories = get_user_categories_query(transaction_type).all()
        return jsonify([{"id": cat.id, "name": cat.name} for cat in categories])
    except Exception as e:
        # TODO: Log error e
        print(f"Error getting categories for form: {e}")
        return jsonify({"error": "Erro ao buscar categorias"}), 500

# --- HTML Routes (Kept for reference, but API is primary) ---
# These might be adapted or removed depending on frontend implementation

@transactions_bp.route("/")
@login_required
def list_transactions_view():
    """View: List transactions (HTML). Likely uses JS to call the API."""
    return render_template("transactions/list.html", title="Transações") # Assumes template exists

@transactions_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_transaction_view():
    """View: Add a new transaction (HTML Form)."""
    form = TransactionForm()
    form.category.query_factory = lambda: get_user_categories_query(form.type.data or TRANSACTION_TYPE_DESPESA)

    if form.validate_on_submit():
        try:
            category = Category.query.get(form.category.data.id)
            if not category or category.type != form.type.data:
                flash(f"Tipo da categoria ({category.type if category else 'N/A'}) não corresponde ao tipo da transação ({form.type.data}).", "danger")
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
            # TODO: Log error e
            print(f"Error adding transaction via form: {e}")
            db.session.rollback()
            flash("Erro ao salvar a transação.", "danger")

    return render_template("transactions/add_edit.html", title="Adicionar Transação", form=form, action_url=url_for('transactions.add_transaction_view'))

@transactions_bp.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction_view(transaction_id: int):
    """View: Edit an existing transaction (HTML Form)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=transaction)
    form.category.query_factory = lambda: get_user_categories_query(form.type.data or transaction.type)

    if form.validate_on_submit():
        try:
            category = Category.query.get(form.category.data.id)
            if not category or category.type != form.type.data:
                flash(f"Tipo da categoria ({category.type if category else 'N/A'}) não corresponde ao tipo da transação ({form.type.data}).", "danger")
                return render_template("transactions/add_edit.html", title="Editar Transação", form=form, transaction_id=transaction_id, action_url=url_for('transactions.edit_transaction_view', transaction_id=transaction_id))

            # Populate object from form
            form.populate_obj(transaction) # Simpler way to update
            # Adjust boolean flags based on type after populate_obj
            transaction.is_paid = form.is_paid.data if transaction.type == TRANSACTION_TYPE_DESPESA else True
            transaction.is_received = form.is_received.data if transaction.type == TRANSACTION_TYPE_RECEITA else True

            db.session.commit()
            flash("Transação atualizada com sucesso!", "success")
            return redirect(url_for("transactions.list_transactions_view"))
        except Exception as e:
            # TODO: Log error e
            print(f"Error editing transaction via form: {e}")
            db.session.rollback()
            flash("Erro ao atualizar a transação.", "danger")

    return render_template("transactions/add_edit.html", title="Editar Transação", form=form, transaction_id=transaction_id, action_url=url_for('transactions.edit_transaction_view', transaction_id=transaction_id))

@transactions_bp.route("/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction_view(transaction_id: int):
    """Action: Delete a transaction (called from HTML form/button)."""
    transaction: Transaction | None = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first()
    if transaction is None:
        flash("Transação não encontrada ou não autorizada.", "warning")
    else:
        try:
            db.session.delete(transaction)
            db.session.commit()
            flash("Transação excluída com sucesso!", "success")
        except Exception as e:
            # TODO: Log error e
            print(f"Error deleting transaction via form: {e}")
            db.session.rollback()
            flash("Erro ao excluir a transação.", "danger")

    return redirect(url_for("transactions.list_transactions_view"))

