# -*- coding: utf-8 -*-
from src.extensions import db
from datetime import datetime

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Allow null user_id for default categories
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    # Type: "Receita" or "Despesa"
    type = db.Column(db.String(10), nullable=False, index=True)
    icon = db.Column(db.String(50)) # Optional icon reference
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship (backref defined in Transaction model)
    # transactions = db.relationship("Transaction", back_populates="category")

    # Relationship to User (for custom categories)
    owner = db.relationship("User", backref=db.backref("categories", lazy="dynamic"))

    def __repr__(self):
        return f"<Category {self.name} ({self.type})>"

