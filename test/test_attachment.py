from .utils import *
from starlette import status
from main import app
from routers.attachment import get_db, get_current_user
from io import BytesIO

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_attachments(test_attachment):
    """Test retrieving attachments for a transaction"""
    response = client.get(f"/attachments/{test_attachment.transaction_id}/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["message"] == "Attachments retrieved successfully"
    assert len(response_data["data"]) == 1

    attachment_data = response_data["data"][0]
    assert attachment_data["id"] == test_attachment.id
    assert attachment_data["transaction_id"] == str(
        test_attachment.transaction_id)
    assert attachment_data["file_path"] == test_attachment.file_path
    assert attachment_data["uploaded_at"] == test_attachment.uploaded_at.isoformat(
    )


def test_get_attachments_empty(test_transaction):
    """Test retrieving attachments when none exist for a transaction"""
    response = client.get(f"/attachments/{test_transaction.id}/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["message"] == "Attachments retrieved successfully"
    assert response_data["data"] == []


def test_add_attachment(test_transaction):
    """Test adding an attachment to a transaction"""
    # Create a mock file
    file_content = b"fake image content"
    files = {"file": ("test_image.jpg", BytesIO(file_content), "image/jpeg")}

    response = client.post(
        f"/attachments/{test_transaction.id}/add", files=files)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Attachment added successfully"

    # Verify the attachment was created in the database
    db = TestSessionLocal()
    attachment = db.query(Attachment).filter(
        Attachment.transaction_id == test_transaction.id
    ).first()

    assert attachment is not None
    assert attachment.transaction_id == test_transaction.id
    assert attachment.file_path == "test_image.jpg"
    assert attachment.uploaded_at is not None

    db.close()


def test_add_attachment_with_different_file_types(test_transaction):
    """Test adding attachments with different file types"""
    test_files = [
        ("receipt.pdf", "application/pdf"),
        ("invoice.png", "image/png"),
        ("document.txt", "text/plain")
    ]

    for filename, content_type in test_files:
        file_content = b"fake file content"
        files = {"file": (filename, BytesIO(file_content), content_type)}

        response = client.post(
            f"/attachments/{test_transaction.id}/add", files=files)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["message"] == "Attachment added successfully"


def test_delete_attachment(test_attachment):
    """Test deleting an attachment"""
    response = client.delete(f"/attachments/{test_attachment.id}/delete")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the attachment was deleted from the database
    db = TestSessionLocal()
    attachment = db.query(Attachment).filter(
        Attachment.id == test_attachment.id
    ).first()
    assert attachment is None

    db.close()


def test_delete_attachment_not_found():
    """Test deleting a non-existent attachment"""
    response = client.delete("/attachments/999/delete")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["message"] == "Attachment not found"


def test_add_multiple_attachments_to_same_transaction(test_transaction):
    """Test adding multiple attachments to the same transaction"""
    # Add first attachment
    files1 = {"file": ("receipt1.jpg", BytesIO(
        b"fake content 1"), "image/jpeg")}
    response1 = client.post(
        f"/attachments/{test_transaction.id}/add", files=files1)
    assert response1.status_code == status.HTTP_201_CREATED

    # Add second attachment
    files2 = {"file": ("receipt2.pdf", BytesIO(
        b"fake content 2"), "application/pdf")}
    response2 = client.post(
        f"/attachments/{test_transaction.id}/add", files=files2)
    assert response2.status_code == status.HTTP_201_CREATED

    # Verify both attachments exist
    response = client.get(f"/attachments/{test_transaction.id}/")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert len(response_data["data"]) == 2

    # Check that both files are present
    file_paths = [attachment["file_path"]
                  for attachment in response_data["data"]]
    assert "receipt1.jpg" in file_paths
    assert "receipt2.pdf" in file_paths


def test_attachment_belongs_to_correct_transaction(test_attachment):
    """Test that attachments are correctly associated with their transactions"""
    # Create another transaction
    db = TestSessionLocal()
    category = db.query(Category).first()

    another_transaction = Transaction(
        user_id=TEST_USER_ID,
        category_id=category.id,
        amount=20000,
        type=TransactionType.EXPENSE,
        payment_method=PaymentMethod.CREDIT_CARD,
        description="Another Test Transaction",
        created_at=datetime.now()
    )

    db.add(another_transaction)
    db.commit()
    db.refresh(another_transaction)

    # Get attachments for the original transaction
    response1 = client.get(f"/attachments/{test_attachment.transaction_id}/")
    assert response1.status_code == status.HTTP_200_OK
    assert len(response1.json()["data"]) == 1

    # Get attachments for the new transaction (should be empty)
    response2 = client.get(f"/attachments/{another_transaction.id}/")
    assert response2.status_code == status.HTTP_200_OK
    assert len(response2.json()["data"]) == 0

    db.close()


def test_add_attachment_without_file(test_transaction):
    """Test adding attachment without providing a file"""
    response = client.post(f"/attachments/{test_transaction.id}/add")
    # This should return a validation error since file is required
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_attachment_cascade_delete_with_transaction(test_attachment):
    """Test that attachments are deleted when their parent transaction is deleted"""
    transaction_id = test_attachment.transaction_id
    attachment_id = test_attachment.id

    # Delete the transaction
    response = client.delete(f"/transactions/{transaction_id}/delete")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the attachment was also deleted (cascade delete)
    db = TestSessionLocal()
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id).first()
    assert attachment is None

    db.close()
