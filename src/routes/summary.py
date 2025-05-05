# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func, extract
from datetime import datetime

from src.extensions import db
from src.models.transaction import Transaction

# Create the blueprint
summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/summary/<int:year>/<int:month>")
@login_required
def get_monthly_summary(year, month):
    """Get summary data (total income, total expenses, balance) for a specific month."""
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

    # Calculate current balance (this might need refinement - based on all transactions up to now?)
    # For simplicity, let's calculate the balance for the month
    month_balance = total_income - total_expenses

    # Calculate overall balance (sum of all transactions for the user)
    # This is a simple calculation, might need adjustment based on initial balances
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
    overall_balance = overall_income - overall_expenses  # Needs initial balances added

    return jsonify(
        {
            "year": year,
            "month": month,
            "total_income": str(total_income),
            "total_expenses": str(total_expenses),
            "month_balance": str(month_balance),
            "overall_balance": str(overall_balance),  # Placeholder, needs refinement
        }
    )


# Add route for pending items if needed, based on is_paid/is_received flags
@summary_bp.route("/summary/pending")
@login_required
def get_pending_summary():
    """Get summary of pending income and expenses."""
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
