# -*- coding: utf-8 -*-
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, Boolean, Text
from decimal import Decimal
from datetime import date

from src.extensions import db # Corrected import path

# Constants for transaction types
TRANSACTION_TYPE_RECEITA = "Receita"
TRANSACTION_TYPE_DESPESA = "Despesa"

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(String(200), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(String(10), nullable=False) # "Receita" or "Despesa"
    date = Column(Date, nullable=False, default=date.today)
    is_paid = Column(Boolean, default=True) # Relevant for Despesa
    is_received = Column(Boolean, default=True) # Relevant for Receita
    # attachment_url = Column(String(255), nullable=True) # Add later if needed

    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.id}: {self.type} - {self.description or \'N/A\'} - {self.amount}>"

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the transaction."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None, # Include account name
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None, # Include category name
            "description": self.description,
            "amount": str(self.amount), # Convert Decimal to string for JSON serialization
            "type": self.type,
            "date": self.date.isoformat(), # Format date as ISO string
            "is_paid": self.is_paid,
            "is_received": self.is_received,
            # "attachment_url": self.attachment_url
        }

    def validate(self):
        """Basic validation logic."""
        if not self.user_id or not self.account_id or not self.category_id:
            raise ValueError("User, Account, and Category are required.")
        if self.amount is None or self.amount <= 0:
            raise ValueError("Amount must be a positive value.")
        if self.type not in [TRANSACTION_TYPE_RECEITA, TRANSACTION_TYPE_DESPESA]:
            raise ValueError(f"Invalid transaction type: {self.type}")
        if not isinstance(self.date, date):
            raise ValueError("Invalid date format.")
        # Add more specific validations as needed

