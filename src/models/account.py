# -*- coding: utf-8 -*-
from src.extensions import db
from datetime import datetime


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(
        db.String(50)
    )  # e.g., "Conta Corrente", "Poupança", "Cartão de Crédito", "Dinheiro"
    initial_balance = db.Column(db.Numeric(10, 2), default=0.00)
    icon = db.Column(db.String(50))  # Optional icon reference
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship (backref defined in Transaction model)
    # transactions = db.relationship("Transaction", back_populates="account")

    # Relationship to User
    owner = db.relationship("User", backref=db.backref("accounts", lazy="dynamic"))

    def __repr__(self):
        return f"<Account {self.name}>"
