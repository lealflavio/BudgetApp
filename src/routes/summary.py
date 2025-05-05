# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func, extract
from datetime import datetime

from src.extensions import db
from src.models.transaction import Transaction

# Create the blueprint
summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/api/summary") # Changed route to /api/summary
@login_required
def get_dashboard_summary():
    """Get summary data for the dashboard (current month and pending items)."""
    now = datetime.utcnow()
    year = now.year
    month = now.month

    # Calculate total income for the current month
    total_income_month = (
        db.session.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "Receita",
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .scalar()
        or 0.00
    )

    # Calculate total expenses for the current month
    total_expenses_month = (
        db.session.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "Despesa",
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .scalar()
        or 0.00
    )

    # Calculate current month balance
    month_balance = total_income_month - total_expenses_month

    # Calculate overall balance (sum of all transactions for the user)
    overall_income = (
        db.session.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == current_user.id, Transaction.type == "Receita")
        .scalar()
        or 0.00
    )
    overall_expenses = (
        db.session.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == current_user.id, Transaction.type == "Despesa")
        .scalar()
        or 0.00
    )
    # Note: This overall balance doesn't account for initial account balances.
    # A more accurate calculation would sum current account balances.
    # For now, we use the sum of transactions.
    overall_balance = overall_income - overall_expenses

    # Get pending items summary
    pending_expenses_query = db.session.query(
        func.sum(Transaction.amount), func.count(Transaction.id)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "Despesa",
        Transaction.is_paid == False,
    )
    pending_expenses_sum, pending_expenses_count = pending_expenses_query.first()

    pending_income_query = db.session.query(
        func.sum(Transaction.amount), func.count(Transaction.id)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "Receita",
        Transaction.is_received == False,
    )
    pending_income_sum, pending_income_count = pending_income_query.first()

    return jsonify(
        {
            "current_month": {
                "year": year,
                "month": month,
                "total_income": str(total_income_month),
                "total_expenses": str(total_expenses_month),
                "month_balance": str(month_balance),
            },
            "overall_balance": str(overall_balance),
            "pending_items": {
                "pending_expenses_total": str(pending_expenses_sum or 0.00),
                "pending_expenses_count": pending_expenses_count or 0,
                "pending_income_total": str(pending_income_sum or 0.00),
                "pending_income_count": pending_income_count or 0,
            }
        }
    )

# Keep old routes for potential future use or direct access if needed
# but they are not used by the main dashboard summary now.
@summary_bp.route("/summary/<int:year>/<int:month>")
@login_required
def get_monthly_summary(year, month):
    # ... (implementation remains the same as before)
    # Calculate total income for the month
    total_income = (
        db.session.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "Receita",
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .scalar()
        or 0.00
    )

    # Calculate total expenses for the month
    total_expenses = (
        db.session.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "Despesa",
            extract("year", Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .scalar()
        or 0.00
    )
    month_balance = total_income - total_expenses
    overall_income = (
        db.session.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == current_user.id, Transaction.type == "Receita")
        .scalar()
        or 0.00
    )
    overall_expenses = (
        db.session.query(func.sum(Transaction.amount))
        .filter(Transaction.user_id == current_user.id, Transaction.type == "Despesa")
        .scalar()
        or 0.00
    )
    overall_balance = overall_income - overall_expenses
    return jsonify(
        {
            "year": year,
            "month": month,
            "total_income": str(total_income),
            "total_expenses": str(total_expenses),
            "month_balance": str(month_balance),
            "overall_balance": str(overall_balance),
        }
    )

@summary_bp.route("/summary/pending")
@login_required
def get_pending_summary():
    # ... (implementation remains the same as before)
    pending_expenses_query = db.session.query(
        func.sum(Transaction.amount), func.count(Transaction.id)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "Despesa",
        Transaction.is_paid == False,
    )
    pending_expenses_sum, pending_expenses_count = pending_expenses_query.first()

    pending_income_query = db.session.query(
        func.sum(Transaction.amount), func.count(Transaction.id)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "Receita",
        Transaction.is_received == False,
    )
    pending_income_sum, pending_income_count = pending_income_query.first()
    return jsonify(
        {
            "pending_expenses_total": str(pending_expenses_sum or 0.00),
            "pending_expenses_count": pending_expenses_count or 0,
            "pending_income_total": str(pending_income_sum or 0.00),
            "pending_income_count": pending_income_count or 0,
        }
    )

