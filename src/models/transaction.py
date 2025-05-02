# -*- coding: utf-8 -*-
from src.extensions import db
from datetime import datetime


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    description = db.Column(db.String(200))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    # Type: "Receita" or "Despesa"
    type = db.Column(db.String(10), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True, default=datetime.utcnow)
    is_paid = db.Column(db.Boolean, default=True)  # For expenses
    is_received = db.Column(db.Boolean, default=True)  # For income
    attachment_url = db.Column(db.String(255))  # Optional attachment URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    owner = db.relationship("User", backref=db.backref("transactions", lazy="dynamic"))
    account = db.relationship(
        "Account", backref=db.backref("transactions", lazy="dynamic")
    )
    category = db.relationship(
        "Category", backref=db.backref("transactions", lazy="dynamic")
    )

    def __repr__(self):
        return f"<Transaction {self.id} ({self.description or 'N/A'})>"
