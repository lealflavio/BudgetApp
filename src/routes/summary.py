# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import func, extract
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Any

from src.extensions import db
from src.models.transaction import Transaction, TRANSACTION_TYPE_DESPESA, TRANSACTION_TYPE_RECEITA

# Create the blueprint
summary_bp = Blueprint("summary", __name__, url_prefix="/summary")

# --- Helper Functions ---
def calculate_balance(user_id: int, account_id: int | None = None, end_date: date | None = None) -> Decimal:
    """Calculates the balance for a user, optionally filtered by account and date.
       Note: This is a simple balance calculation (Income - Expenses). It does not
       consider initial account balances. For a true account balance, a different
       approach tracking initial balance + transactions is needed.
    """
    # Sum of income
    income_query = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == TRANSACTION_TYPE_RECEITA
    )
    # Sum of expenses
    expense_query = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == TRANSACTION_TYPE_DESPESA
    )

    if account_id:
        income_query = income_query.filter(Transaction.account_id == account_id)
        expense_query = expense_query.filter(Transaction.account_id == account_id)

    if end_date:
        income_query = income_query.filter(Transaction.date <= end_date)
        expense_query = expense_query.filter(Transaction.date <= end_date)

    total_income: Decimal | None = income_query.scalar()
    total_expense: Decimal | None = expense_query.scalar()

    balance = (total_income or Decimal(0)) - (total_expense or Decimal(0))
    return balance

# --- API Routes ---
@summary_bp.route("/api/balance", methods=["GET"])
@login_required
def api_get_balance():
    """API: Get the current overall balance (Income - Expenses) for the user (JSON).
       Accepts optional 'account_id' and 'end_date' (YYYY-MM-DD) query parameters.
    """
    try:
        account_id = request.args.get("account_id", type=int)
        end_date_str = request.args.get("end_date")
        end_date_obj: date | None = None

        if end_date_str:
            try:
                end_date_obj = date.fromisoformat(end_date_str)
            except ValueError:
                return jsonify({"error": "Formato de data final inválido (YYYY-MM-DD)"}), 400

        balance = calculate_balance(current_user.id, account_id=account_id, end_date=end_date_obj)
        return jsonify({
            "balance": str(balance), # Convert Decimal to string
            "account_id_filter": account_id,
            "end_date_filter": end_date_str
        })
    except Exception as e:
        # TODO: Log error e
        print(f"Error calculating balance: {e}")
        return jsonify({"error": "Erro ao calcular saldo"}), 500

@summary_bp.route("/api/monthly", methods=["GET"])
@login_required
def api_get_monthly_summary():
    """API: Get income and expenses for a specific month (JSON).
       Accepts optional 'year' and 'month' query parameters.
       Defaults to the current month.
    """
    try:
        current_dt = date.today()
        year = request.args.get("year", default=current_dt.year, type=int)
        month = request.args.get("month", default=current_dt.month, type=int)

        # Validate month and year
        if not (1 <= month <= 12):
            return jsonify({"error": "Mês inválido"}), 400
        # Add year validation if needed (e.g., range)

        # Base query for the month
        base_query = db.session.query(
            func.sum(func.coalesce(Transaction.amount, 0)).label("total")
        ).filter(
            Transaction.user_id == current_user.id,
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month
        )

        # Calculate total income for the month
        monthly_income_query = base_query.filter(Transaction.type == TRANSACTION_TYPE_RECEITA)
        monthly_income: Decimal | None = monthly_income_query.scalar()

        # Calculate total expenses for the month
        monthly_expense_query = base_query.filter(Transaction.type == TRANSACTION_TYPE_DESPESA)
        monthly_expense: Decimal | None = monthly_expense_query.scalar()

        monthly_balance = (monthly_income or Decimal(0)) - (monthly_expense or Decimal(0))

        return jsonify({
            "year": year,
            "month": month,
            "total_income": str(monthly_income or Decimal(0)),
            "total_expense": str(monthly_expense or Decimal(0)),
            "monthly_balance": str(monthly_balance)
        })

    except Exception as e:
        # TODO: Log error e
        print(f"Error calculating monthly summary: {e}")
        return jsonify({"error": "Erro ao calcular resumo mensal"}), 500

@summary_bp.route("/api/pending", methods=["GET"])
@login_required
def api_get_pending_summary():
    """API: Get summary of pending (unpaid/unreceived) transactions (JSON)."""
    try:
        # Pending Expenses (Despesas not paid)
        pending_expenses_query = db.session.query(
            func.sum(func.coalesce(Transaction.amount, 0)).label("total"),
            func.count(Transaction.id).label("count") # Count the items
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TRANSACTION_TYPE_DESPESA,
            Transaction.is_paid == False
        )
        pending_expenses_result = pending_expenses_query.first()
        total_pending_expenses = pending_expenses_result.total if pending_expenses_result else Decimal(0)
        count_pending_expenses = pending_expenses_result.count if pending_expenses_result else 0

        # Pending Income (Receitas not received)
        pending_income_query = db.session.query(
            func.sum(func.coalesce(Transaction.amount, 0)).label("total"),
            func.count(Transaction.id).label("count") # Count the items
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TRANSACTION_TYPE_RECEITA,
            Transaction.is_received == False
        )
        pending_income_result = pending_income_query.first()
        total_pending_income = pending_income_result.total if pending_income_result else Decimal(0)
        count_pending_income = pending_income_result.count if pending_income_result else 0

        return jsonify({
            "total_pending_expenses": str(total_pending_expenses or Decimal(0)),
            "count_pending_expenses": count_pending_expenses,
            "total_pending_income": str(total_pending_income or Decimal(0)),
            "count_pending_income": count_pending_income
        })

    except Exception as e:
        # TODO: Log error e
        print(f"Error calculating pending summary: {e}")
        return jsonify({"error": "Erro ao calcular resumo de pendências"}), 500

# --- HTML Routes (Kept for reference, could be part of a dashboard) ---
@summary_bp.route("/")
@login_required
def summary_dashboard_view():
    """View: Display summary information (HTML). Likely uses JS to call APIs."""
    # This view would typically fetch data via JS calls to the API endpoints above
    return render_template("summary/dashboard.html", title="Resumo Financeiro") # Assumes template exists

