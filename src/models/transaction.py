# -*- coding: utf-8 -*-
from src.extensions import db
from datetime import datetime, date
from decimal import Decimal
from typing import TYPE_CHECKING

# Constants for transaction types
TRANSACTION_TYPE_RECEITA = "Receita"
TRANSACTION_TYPE_DESPESA = "Despesa"

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.account import Account
    from src.models.category import Category

class Transaction(db.Model):
    __tablename__ = "transaction" # Explicit table name recommended

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    account_id: int = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    category_id: int = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    description: str | None = db.Column(db.String(200))
    amount: Decimal = db.Column(db.Numeric(10, 2), nullable=False)
    # Type: "Receita" or "Despesa"
    type: str = db.Column(db.String(10), nullable=False, index=True)
    date: date = db.Column(db.Date, nullable=False, index=True, default=datetime.utcnow)
    # Consider renaming is_paid/is_received to is_pending or is_settled for clarity,
    # but keeping original names for now as per initial code.
    is_paid: bool = db.Column(db.Boolean, default=True) # For expenses
    is_received: bool = db.Column(db.Boolean, default=True) # For income
    attachment_url: str | None = db.Column(db.String(255)) # Optional attachment URL
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    owner: "User" = db.relationship("User", backref=db.backref("transactions", lazy="dynamic"))
    account: "Account" = db.relationship("Account", backref=db.backref("transactions", lazy="dynamic"))
    category: "Category" = db.relationship("Category", backref=db.backref("transactions", lazy="dynamic"))

    def __repr__(self) -> str:
        return f"<Transaction {self.id} ({self.description or 'N/A'})>"

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the transaction."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "category_id": self.category_id,
            "description": self.description,
            "amount": str(self.amount), # Return as string for JSON consistency
            "type": self.type,
            "date": self.date.isoformat(),
            "is_paid": self.is_paid,
            "is_received": self.is_received,
            "attachment_url": self.attachment_url,
            "created_at": self.created_at.isoformat(),
            "account_name": self.account.name if self.account else None,
            "category_name": self.category.name if self.category else None
        }

