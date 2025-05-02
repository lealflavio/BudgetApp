# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from wtforms import StringField, SelectField, BooleanField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Optional

from src.extensions import db
from src.models.category import Category

# Create the blueprint
categories_bp = Blueprint("categories", __name__, template_folder="../static")

# --- Forms ---
class CategoryForm(FlaskForm):
    name = StringField("Nome da Categoria", validators=[DataRequired(), Length(max=100)])
    type = SelectField("Tipo", choices=[
        ("Despesa", "Despesa"),
        ("Receita", "Receita")
    ], validators=[DataRequired()])
    icon = StringField("Ícone (Opcional)", validators=[Optional(), Length(max=50)])
    # is_default is handled internally, not by user form
    submit = SubmitField("Salvar Categoria")

# --- Routes ---
@categories_bp.route("/categories")
@login_required
def list_categories():
    """List all default categories and categories for the current user."""
    # Query default categories (user_id is None) and user-specific categories
    user_categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.is_default == True)
    ).order_by(Category.type, Category.name).all()

    # For now, returning JSON, will integrate with template later
    return jsonify([{
        "id": cat.id,
        "name": cat.name,
        "type": cat.type,
        "is_default": cat.is_default,
        "user_id": cat.user_id
    } for cat in user_categories])

@categories_bp.route("/categories/add", methods=["GET", "POST"])
@login_required
def add_category():
    """Add a new custom category for the current user."""
    form = CategoryForm()
    if form.validate_on_submit():
        # Check if category with the same name and type already exists for the user
        existing_category = Category.query.filter_by(
            user_id=current_user.id,
            name=form.name.data,
            type=form.type.data
        ).first()
        if existing_category:
            flash("Você já possui uma categoria com este nome e tipo.")
        else:
            new_category = Category(
                user_id=current_user.id,
                name=form.name.data,
                type=form.type.data,
                icon=form.icon.data,
                is_default=False # Custom categories are not default
            )
            db.session.add(new_category)
            db.session.commit()
            flash("Categoria adicionada com sucesso!")
            return redirect(url_for("categories.list_categories")) # Redirect to list view

    # Render a template with the form (to be created)
    # return render_template("add_category.html", title="Adicionar Categoria", form=form)
    # Temporary response
    return jsonify({"message": "GET request to add_category. Use POST to submit form."})

@categories_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    """Edit an existing custom category."""
    category = Category.query.get_or_404(category_id)
    # Ensure the user owns this category and it's not a default one
    if category.user_id != current_user.id or category.is_default:
        flash("Acesso não autorizado ou categoria padrão não pode ser editada.")
        return redirect(url_for("categories.list_categories"))

    form = CategoryForm(obj=category) # Pre-populate form
    if form.validate_on_submit():
        # Check if changing name/type conflicts with another existing category for the user
        existing_category = Category.query.filter(
            Category.id != category_id, # Exclude the current category
            Category.user_id == current_user.id,
            Category.name == form.name.data,
            Category.type == form.type.data
        ).first()
        if existing_category:
            flash("Você já possui outra categoria com este nome e tipo.")
        else:
            category.name = form.name.data
            category.type = form.type.data
            category.icon = form.icon.data
            db.session.commit()
            flash("Categoria atualizada com sucesso!")
            return redirect(url_for("categories.list_categories"))

    # Render a template with the form (to be created)
    # return render_template("edit_category.html", title="Editar Categoria", form=form, category_id=category_id)
    # Temporary response
    return jsonify({"message": f"GET request to edit_category {category_id}. Use POST to submit form."})

@categories_bp.route("/categories/delete/<int:category_id>", methods=["POST"]) # Use POST for deletion
@login_required
def delete_category(category_id):
    """Delete a custom category."""
    category = Category.query.get_or_404(category_id)
    # Ensure the user owns this category and it's not a default one
    if category.user_id != current_user.id or category.is_default:
        flash("Acesso não autorizado ou categoria padrão não pode ser excluída.")
        return redirect(url_for("categories.list_categories"))

    # Check for associated transactions before deleting (important!)
    # Need Transaction model and relationship defined first
    # if category.transactions.count() > 0:
    #     flash("Não é possível excluir categorias com transações associadas. Reatribua as transações primeiro.")
    #     return redirect(url_for("categories.list_categories"))

    db.session.delete(category)
    db.session.commit()
    flash("Categoria excluída com sucesso!")
    return redirect(url_for("categories.list_categories"))

