from fastapi import APIRouter, Depends, UploadFile, File, status
from db.models import Attachment
from routers.auth import db_dependency, get_current_user
from db.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from core.validation import validate_user
from pydantic import BaseModel
from datetime import datetime
from core.base_response import SuccessResponse, ErrorResponse
import uuid

router = APIRouter(
    prefix="/attachments",
    tags=["attachments"],
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class AttachmentResponse(BaseModel):
    id: int
    transaction_id: uuid.UUID
    file_path: str
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }


def get_attachment_response(attachments):
    for attachment in attachments:
        yield AttachmentResponse.model_validate(attachment)


@router.get("/{transaction_id}/", status_code=status.HTTP_200_OK)
async def get_attachments(db: db_dependency, user: user_dependency, transaction_id: str):
    validate_user(user)
    transaction_uuid = uuid.UUID(transaction_id)
    attachments = db.query(Attachment).filter(
        Attachment.transaction_id == transaction_uuid).all()
    attachment_responses = get_attachment_response(attachments)
    return SuccessResponse(message="Attachments retrieved successfully", data=attachment_responses)


@router.post("/{transaction_id}/add", status_code=status.HTTP_201_CREATED)
async def add_attachment(db: db_dependency, user: user_dependency, transaction_id: str, file: UploadFile = File(...)):
    validate_user(user)
    transaction_uuid = uuid.UUID(transaction_id)
    attachment = Attachment(
        transaction_id=transaction_uuid,
        file_path=file.filename,
        uploaded_at=datetime.now()
    )
    db.add(attachment)
    db.commit()

    return SuccessResponse(message="Attachment added successfully")


@router.delete("/{attachment_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(db: db_dependency, user: user_dependency, attachment_id: int):
    validate_user(user)
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id).first()
    if not attachment:
        raise ErrorResponse(
            message="Attachment not found", status_code=status.HTTP_404_NOT_FOUND)
    db.delete(attachment)
    db.commit()
