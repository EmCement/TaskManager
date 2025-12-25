from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import crud
import schemas
from auth import get_current_user

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.get("/task/{task_id}", response_model=List[schemas.AttachmentWithUser])
async def read_attachments_by_task(
        task_id: int,
        current_user=Depends(get_current_user)
):
    """Получить все вложения по задаче (только если есть доступ к задаче)"""
    # Проверяем доступ к задаче
    db_task = await crud.get_task(
        task_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")

    attachments = await crud.get_attachments_by_task(task_id=task_id)
    return attachments


@router.get("/{attachment_id}", response_model=schemas.Attachment)
async def read_attachment(
        attachment_id: int,
        current_user=Depends(get_current_user)
):
    """Получить вложение по ID"""
    db_attachment = await crud.get_attachment(attachment_id=attachment_id)
    if db_attachment is None:
        raise HTTPException(status_code=404, detail="Вложение не найдено")

    # Проверяем доступ к задаче вложения
    db_task = await crud.get_task(
        db_attachment.task_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Нет доступа к этому вложению")

    return db_attachment


@router.post("/", response_model=schemas.Attachment, status_code=status.HTTP_201_CREATED)
async def create_attachment(
        attachment: schemas.AttachmentCreate,
        current_user=Depends(get_current_user)
):
    """Создать новое вложение (только если есть доступ к задаче)"""
    # Проверяем доступ к задаче
    db_task = await crud.get_task(
        attachment.task_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")

    return await crud.create_attachment(attachment=attachment, user_id=current_user.id)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
        attachment_id: int,
        current_user=Depends(get_current_user)
):
    """Удалить вложение (только свое или админ может все)"""
    db_attachment = await crud.get_attachment(attachment_id=attachment_id)
    if db_attachment is None:
        raise HTTPException(status_code=404, detail="Вложение не найдено")

    # Проверяем доступ к задаче
    db_task = await crud.get_task(
        db_attachment.task_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Нет доступа к этому вложению")

    # Проверяем, что пользователь удаляет свое вложение
    if db_attachment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете удалять только свои вложения"
        )

    await crud.delete_attachment(attachment_id=attachment_id)
    return None
