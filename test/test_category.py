from starlette import status

from .utils import *
from main import app
from routers.category import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_categories(test_category):
    response = client.get("/categories")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Categories retrieved successfully",
        "data": [
            {
                "id": 1,
                "name": "Test Category"
            }
        ]
    }

def test_create_category(test_category):
    request_body = {
        "name": "New Test Category"
    }

    response = client.post("/categories/add", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "message": "Category created successfully",
        "data": {
            "id": 2,
            "name": "New Test Category"
        }
    }

def test_update_category(test_category):
    request_body = {
        "name": "Updated Category"
    }

    response = client.put("/categories/1/update", json=request_body)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    category = db.query(Category).filter(Category.id == 1).first()

    assert category.name == "Updated Category"

    db.close()

def test_update_category_not_found(test_category):
    request_body = {
        "name": "Updated Category"
    }
    response = client.put("/categories/100/update", json=request_body)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_category(test_category):
    response = client.delete("/categories/1/delete")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestSessionLocal()
    category = db.query(Category).filter(Category.id == 1).first()
    
    assert category is None

    db.close()

def test_delete_category_not_found(test_category):
    response = client.delete("/categories/100/delete")
    assert response.status_code == status.HTTP_404_NOT_FOUND