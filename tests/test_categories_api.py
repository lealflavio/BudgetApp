# -*- coding: utf-8 -*-
import json
from src.models.category import Category
from src.models.user import User # Needed for creating another user

def test_list_categories_initial(client, logged_in_user, init_database):
    """Test listing categories when only defaults might exist (or none)."""
    # Assuming no default categories are pre-populated by migrations in test env
    # If defaults ARE created, this test needs adjustment
    db = init_database
    # Optionally create default categories if they aren't auto-created
    default_cat = Category(name="Salário", type="Receita", is_default=True)
    db.session.add(default_cat)
    db.session.commit()

    res = client.get("/categories")
    assert res.status_code == 200
    # Should contain at least the default category
    assert len(res.json) >= 1
    assert any(cat["name"] == "Salário" and cat["is_default"] for cat in res.json)

def test_add_category_success(client, logged_in_user, init_database):
    """Test successfully adding a new custom category."""
    data = {
        "name": "Alimentação",
        "type": "Despesa",
        "icon": "utensils"
    }
    res = client.post("/categories", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 201
    assert res.json["name"] == data["name"]
    assert res.json["type"] == data["type"]
    assert res.json["icon"] == data["icon"]
    assert res.json["is_default"] == False
    assert res.json["user_id"] == logged_in_user.id

    # Verify in DB
    category = Category.query.filter_by(user_id=logged_in_user.id, name=data["name"]).first()
    assert category is not None
    assert category.type == data["type"]
    assert not category.is_default

def test_add_category_duplicate(client, logged_in_user, init_database):
    """Test adding a category with the same name and type for the same user."""
    # Add first category
    cat1 = Category(user_id=logged_in_user.id, name="Transporte", type="Despesa", is_default=False)
    db = init_database
    db.session.add(cat1)
    db.session.commit()

    # Try adding duplicate
    data = {
        "name": "Transporte",
        "type": "Despesa",
        "icon": "bus"
    }
    res = client.post("/categories", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 409 # Conflict
    assert "already exists" in res.json["error"]

def test_add_category_invalid_type(client, logged_in_user):
    """Test adding category with invalid type."""
    data = {
        "name": "Lazer",
        "type": "Gasto", # Invalid type
        "icon": "gamepad"
    }
    res = client.post("/categories", data=json.dumps(data), content_type="application/json")
    assert res.status_code == 400
    assert "Invalid or missing \'type\'" in res.json["error"]

def test_list_categories_mixed(client, logged_in_user, init_database):
    """Test listing categories including default and user-specific."""
    db = init_database
    # Add default and user categories
    default_cat = Category(name="Moradia", type="Despesa", is_default=True)
    user_cat = Category(user_id=logged_in_user.id, name="Educação", type="Despesa", is_default=False)
    db.session.add_all([default_cat, user_cat])
    db.session.commit()

    res = client.get("/categories")
    assert res.status_code == 200
    assert len(res.json) >= 2 # At least the two we added

    names = {cat["name"] for cat in res.json}
    assert "Moradia" in names
    assert "Educação" in names

    default_found = any(cat["name"] == "Moradia" and cat["is_default"] for cat in res.json)
    user_found = any(cat["name"] == "Educação" and not cat["is_default"] and cat["user_id"] == logged_in_user.id for cat in res.json)
    assert default_found
    assert user_found

def test_get_category_success_user(client, logged_in_user, init_database):
    """Test getting a specific user-owned category."""
    cat = Category(user_id=logged_in_user.id, name="Saúde", type="Despesa", is_default=False)
    db = init_database
    db.session.add(cat)
    db.session.commit()

    res = client.get(f"/categories/{cat.id}")
    assert res.status_code == 200
    assert res.json["id"] == cat.id
    assert res.json["name"] == "Saúde"
    assert not res.json["is_default"]

def test_get_category_success_default(client, logged_in_user, init_database):
    """Test getting a specific default category."""
    cat = Category(name="Investimento Retorno", type="Receita", is_default=True)
    db = init_database
    db.session.add(cat)
    db.session.commit()

    res = client.get(f"/categories/{cat.id}")
    assert res.status_code == 200
    assert res.json["id"] == cat.id
    assert res.json["name"] == "Investimento Retorno"
    assert res.json["is_default"]

def test_get_category_not_found(client, logged_in_user):
    """Test getting a non-existent category."""
    res = client.get("/categories/999")
    assert res.status_code == 404

def test_get_category_unauthorized(client, logged_in_user, init_database):
    """Test getting a category owned by another user."""
    other_user = User(username="otheruser_cat", email="other_cat@example.com")
    other_user.set_password("password")
    db = init_database
    db.session.add(other_user)
    db.session.commit()
    other_cat = Category(user_id=other_user.id, name="Other User Cat", type="Despesa", is_default=False)
    db.session.add(other_cat)
    db.session.commit()

    res = client.get(f"/categories/{other_cat.id}")
    assert res.status_code == 403 # Unauthorized

def test_update_category_success(client, logged_in_user, init_database):
    """Test successfully updating a custom category."""
    cat = Category(user_id=logged_in_user.id, name="Old Cat Name", type="Receita", is_default=False)
    db = init_database
    db.session.add(cat)
    db.session.commit()

    update_data = {
        "name": "New Cat Name",
        "type": "Despesa", # Change type
        "icon": "new-icon"
    }
    res = client.put(f"/categories/{cat.id}", data=json.dumps(update_data), content_type="application/json")
    assert res.status_code == 200
    assert res.json["name"] == update_data["name"]
    assert res.json["type"] == update_data["type"]
    assert res.json["icon"] == update_data["icon"]

    # Verify in DB
    updated_cat = Category.query.get(cat.id)
    assert updated_cat.name == update_data["name"]
    assert updated_cat.type == update_data["type"]

def test_update_category_conflict(client, logged_in_user, init_database):
    """Test updating a category to a name/type that already exists for the user."""
    db = init_database
    cat1 = Category(user_id=logged_in_user.id, name="Unique Name 1", type="Despesa", is_default=False)
    cat2 = Category(user_id=logged_in_user.id, name="Unique Name 2", type="Despesa", is_default=False)
    db.session.add_all([cat1, cat2])
    db.session.commit()

    update_data = {
        "name": "Unique Name 1", # Try to rename cat2 to cat1's name/type
        "type": "Despesa",
        "icon": ""
    }
    res = client.put(f"/categories/{cat2.id}", data=json.dumps(update_data), content_type="application/json")
    assert res.status_code == 409 # Conflict
    assert "already exists" in res.json["error"]

def test_update_category_default_forbidden(client, logged_in_user, init_database):
    """Test attempting to update a default category."""
    cat = Category(name="Default Cannot Change", type="Receita", is_default=True)
    db = init_database
    db.session.add(cat)
    db.session.commit()

    update_data = {"name": "Changed Default", "type": "Receita", "icon": ""}
    res = client.put(f"/categories/{cat.id}", data=json.dumps(update_data), content_type="application/json")
    assert res.status_code == 403 # Forbidden
    assert "Cannot edit default categories" in res.json["error"]

def test_update_category_unauthorized(client, logged_in_user, init_database):
    """Test updating a category owned by another user."""
    other_user = User(username="otheruser_cat2", email="other_cat2@example.com")
    other_user.set_password("password")
    db = init_database
    db.session.add(other_user)
    db.session.commit()
    other_cat = Category(user_id=other_user.id, name="Other User Cat Edit", type="Despesa", is_default=False)
    db.session.add(other_cat)
    db.session.commit()

    update_data = {"name": "Hacked Cat", "type": "Despesa", "icon": ""}
    res = client.put(f"/categories/{other_cat.id}", data=json.dumps(update_data), content_type="application/json")
    assert res.status_code == 403 # Forbidden

def test_delete_category_success(client, logged_in_user, init_database):
    """Test successfully deleting a custom category."""
    cat = Category(user_id=logged_in_user.id, name="To Delete Cat", type="Despesa", is_default=False)
    db = init_database
    db.session.add(cat)
    db.session.commit()
    category_id = cat.id

    res = client.delete(f"/categories/{category_id}")
    assert res.status_code == 200
    assert "Category deleted successfully" in res.json["message"]

    # Verify in DB
    deleted_cat = Category.query.get(category_id)
    assert deleted_cat is None

def test_delete_category_default_forbidden(client, logged_in_user, init_database):
    """Test attempting to delete a default category."""
    cat = Category(name="Default Cannot Delete", type="Receita", is_default=True)
    db = init_database
    db.session.add(cat)
    db.session.commit()

    res = client.delete(f"/categories/{cat.id}")
    assert res.status_code == 403 # Forbidden
    assert "Cannot delete default categories" in res.json["error"]

def test_delete_category_unauthorized(client, logged_in_user, init_database):
    """Test deleting a category owned by another user."""
    other_user = User(username="otheruser_cat3", email="other_cat3@example.com")
    other_user.set_password("password")
    db = init_database
    db.session.add(other_user)
    db.session.commit()
    other_cat = Category(user_id=other_user.id, name="Other User Cat Delete", type="Despesa", is_default=False)
    db.session.add(other_cat)
    db.session.commit()

    res = client.delete(f"/categories/{other_cat.id}")
    assert res.status_code == 403 # Forbidden

def test_delete_category_not_found(client, logged_in_user):
    """Test deleting a non-existent category."""
    res = client.delete("/categories/999")
    assert res.status_code == 404

# TODO: Add test case for deleting category with transactions if that logic is implemented

