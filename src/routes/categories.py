# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required

from src.extensions import db
from src.models.category import Category

# Create the blueprint
categories_bp = Blueprint("categories", __name__)

# --- Helper Function ---
def category_to_dict(category):
    """Converts a Category object to a dictionary for JSON serialization."""
    return {
        "id": category.id,
        "user_id": category.user_id, # Can be None for default categories
        "name": category.name,
        "type": category.type, # "Receita" or "Despesa"
        "icon": category.icon,
        "is_default": category.is_default,
        "created_at": category.created_at.isoformat() # Use ISO format for datetime
    }

# --- Routes ---
@categories_bp.route("/categories", methods=["GET"])
@login_required
def list_categories():
    """API endpoint to list all default categories and categories for the current user."""
    try:
        # Query default categories (is_default == True) and user-specific categories
        user_and_default_categories = Category.query.filter(
            (Category.user_id == current_user.id) | (Category.is_default == True)
        ).order_by(Category.type, Category.name).all()
        return jsonify([category_to_dict(cat) for cat in user_and_default_categories]), 200
    except Exception as e:
        # Log the error e
        return jsonify({"error": "An unexpected error occurred"}), 500

@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
@login_required
def get_category(category_id):
    """API endpoint to get a specific category by ID."""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category not found"}), 404
        # Allow access if it's a default category or belongs to the user
        if not category.is_default and category.user_id != current_user.id:
            return jsonify({"error": "Unauthorized access"}), 403
        return jsonify(category_to_dict(category)), 200
    except Exception as e:
        # Log the error e
        return jsonify({"error": "An unexpected error occurred"}), 500

@categories_bp.route("/categories", methods=["POST"])
@login_required
def add_category():
    """API endpoint to add a new custom category for the current user."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input, JSON required"}), 400

    name = data.get("name")
    category_type = data.get("type")
    icon = data.get("icon")

    # Basic Validation
    if not name or not isinstance(name, str) or len(name) > 100:
        return jsonify({"error": "Invalid or missing 'name'"}), 400
    if not category_type or category_type not in ["Receita", "Despesa"]:
        return jsonify({"error": "Invalid or missing 'type'. Must be 'Receita' or 'Despesa'."}), 400
    if icon and (not isinstance(icon, str) or len(icon) > 50):
        return jsonify({"error": "Invalid 'icon'"}), 400

    try:
        # Check if category with the same name and type already exists for the user
        existing_category = Category.query.filter_by(
            user_id=current_user.id,
            name=name,
            type=category_type
        ).first()
        if existing_category:
            return jsonify({"error": "A category with this name and type already exists for this user"}), 409 # 409 Conflict

        new_category = Category(
            user_id=current_user.id,
            name=name,
            type=category_type,
            icon=icon,
            is_default=False # Custom categories are never default
        )
        db.session.add(new_category)
        db.session.commit()
        return jsonify(category_to_dict(new_category)), 201 # 201 Created status
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"error": "Failed to add category"}), 500

@categories_bp.route("/categories/<int:category_id>", methods=["PUT"])
@login_required
def update_category(category_id):
    """API endpoint to update an existing custom category (full update)."""
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    # Prevent editing default categories or categories not owned by the user
    if category.is_default or category.user_id != current_user.id:
        return jsonify({"error": "Unauthorized: Cannot edit default categories or categories owned by others"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input, JSON required"}), 400

    name = data.get("name")
    category_type = data.get("type")
    icon = data.get("icon")

    # Basic Validation (similar to POST, ensure all required fields for PUT are present)
    if not name or not isinstance(name, str) or len(name) > 100:
        return jsonify({"error": "Invalid or missing 'name'"}), 400
    if not category_type or category_type not in ["Receita", "Despesa"]:
        return jsonify({"error": "Invalid or missing 'type'. Must be 'Receita' or 'Despesa'."}), 400
    if icon and (not isinstance(icon, str) or len(icon) > 50):
        return jsonify({"error": "Invalid 'icon'"}), 400

    try:
        # Check if changing name/type conflicts with another existing category for the user
        existing_category = Category.query.filter(
            Category.id != category_id, # Exclude the current category being updated
            Category.user_id == current_user.id,
            Category.name == name,
            Category.type == category_type
        ).first()
        if existing_category:
            return jsonify({"error": "Another category with this name and type already exists for this user"}), 409 # 409 Conflict

        category.name = name
        category.type = category_type
        category.icon = icon
        db.session.commit()
        return jsonify(category_to_dict(category)), 200
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"error": "Failed to update category"}), 500

@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@login_required
def delete_category(category_id):
    """API endpoint to delete a custom category."""
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    # Prevent deleting default categories or categories not owned by the user
    if category.is_default or category.user_id != current_user.id:
        return jsonify({"error": "Unauthorized: Cannot delete default categories or categories owned by others"}), 403

    # Optional: Check for associated transactions before deleting
    # from src.models.transaction import Transaction # Import here or globally if needed
    # if Transaction.query.filter_by(category_id=category_id).first():
    #     return jsonify({"error": "Cannot delete category with associated transactions"}), 400

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted successfully"}), 200 # Or 204 No Content
    except Exception as e:
        db.session.rollback()
        # Log the error e
        return jsonify({"error": "Failed to delete category"}), 500

# Remove form-based routes or comment them out if needed temporarily
# class CategoryForm(FlaskForm): ...
# @categories_bp.route("/categories/add", methods=["GET", "POST"]) ...
# @categories_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"]) ...
# @categories_bp.route("/categories/delete/<int:category_id>", methods=["POST"]) ...

