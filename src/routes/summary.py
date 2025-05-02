# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request # Added request
from flask_login import current_user, login_required
from sqlalchemy import func, extract, and_
from datetime import datetime, date
from decimal import Decimal

from src.extensions import db # Corrected import path
from src.models.transaction import Transaction, TRANSACTION_TYPE_RECEITA, TRANSACTION_TYPE_DESPESA
from src.models.account import Account # Needed for potential future balance calculations

# Create the blueprint
summary_bp = Blueprint("summary", __name__, url_prefix="/summary")

def _get_month_range(year: int, month: int) -> tuple[date, date]:
    """Calculates the start and end date for a given year and month."""
    start_date = date(year, month, 1)
    # Calculate the first day of the next month
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    return start_date, end_date

@summary_bp.route("/api/monthly", methods=["GET"])
@login_required
def api_get_monthly_summary():
    """API endpoint to get summary data for a specific month/year from query params."""
    try:
        year = int(request.args.get("year", datetime.utcnow().year))
        month = int(request.args.get("month", datetime.utcnow().month))
        if not (1 <= month <= 12):
            return jsonify({"error": "Mês inválido"}), 400
    except ValueError:
        return jsonify({"error": "Ano ou mês inválido"}), 400

    start_date, end_date = _get_month_range(year, month)

    try:
        # Calculate total income for the month
        total_income_query = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TRANSACTION_TYPE_RECEITA,
            Transaction.date >= start_date,
            Transaction.date < end_date
        )
        total_income: Decimal = total_income_query.scalar() or Decimal("0.00")

        # Calculate total expenses for the month
        total_expenses_query = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TRANSACTION_TYPE_DESPESA,
            Transaction.date >= start_date,
            Transaction.date < end_date
        )
        total_expenses: Decimal = total_expenses_query.scalar() or Decimal("0.00")

        # Calculate balance for the month
        month_balance: Decimal = total_income - total_expenses

        # --- Refined Overall Balance Calculation ---
        # Calculate the balance of all transactions *before* the start of the requested month
        previous_income = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TRANSACTION_TYPE_RECEITA,
            Transaction.date < start_date
        ).scalar() or Decimal("0.00")

        previous_expenses = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TRANSACTION_TYPE_DESPESA,
            Transaction.date < start_date
        ).scalar() or Decimal("0.00")

        # Consider initial account balances if available (future enhancement)
        # initial_balance = db.session.query(func.sum(Account.initial_balance)).filter(...).scalar() or Decimal("0.00")
        initial_balance = Decimal("0.00") # Placeholder

        balance_at_month_start = initial_balance + previous_income - previous_expenses
        balance_at_month_end = balance_at_month_start + month_balance

        return jsonify({
            "year": year,
            "month": month,
            "total_income": str(total_income),
            "total_expenses": str(total_expenses),
            "month_balance": str(month_balance),
            "balance_at_start": str(balance_at_month_start), # Balance at the beginning of the month
            "balance_at_end": str(balance_at_month_end)     # Balance at the end of the month
        })
    except Exception as e:
        # Log error e
        return jsonify({"error": "Erro interno ao calcular o resumo mensal"}), 500

@summary_bp.route("/api/pending", methods=["GET"])
@login_required
def api_get_pending_summary():
    """API endpoint to get summary of pending income and expenses."""
    try:
        pending_expenses_query = db.session.query(
            func.sum(Transaction.amount),
            func.count(Transaction.id)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TRANSACTION_TYPE_DESPESA,
            Transaction.is_paid == False
        )
        pending_expenses_sum, pending_expenses_count = pending_expenses_query.first()

        pending_income_query = db.session.query(
            func.sum(Transaction.amount),
            func.count(Transaction.id)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TRANSACTION_TYPE_RECEITA,
            Transaction.is_received == False
        )
        pending_income_sum, pending_income_count = pending_income_query.first()

        return jsonify({
            "pending_expenses_total": str(pending_expenses_sum or Decimal("0.00")),
            "pending_expenses_count": pending_expenses_count or 0,
            "pending_income_total": str(pending_income_sum or Decimal("0.00")),
            "pending_income_count": pending_income_count or 0
        })
    except Exception as e:
        # Log error e
        return jsonify({"error": "Erro interno ao calcular o resumo de pendências"}), 500

# Deprecated route - Use /api/monthly with query parameters
# @summary_bp.route("/summary/<int:year>/<int:month>")
# @login_required
# def get_monthly_summary(year, month):
#     # ... (old implementation) ...
#     pass

# Deprecated route - Use /api/pending
# @summary_bp.route("/summary/pending")
# @login_required
# def get_pending_summary():
#    # ... (old implementation) ...
#    pass

