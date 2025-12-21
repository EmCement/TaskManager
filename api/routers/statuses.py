from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import crud
import schemas
from auth import get_current_user, require_admin

router = APIRouter(prefix="/statuses", tags=["statuses"])


@router.get("/", response_model=List[schemas.Status])
async def read_statuses(current_user = Depends(get_current_user)):
    """Получить список всех статусов"""
    statuses = await crud.get_statuses()
    return statuses


@router.get("/{status_id}", response_model=schemas.Status)
async def read_status(
    status_id: int,
    current_user = Depends(get_current_user)
):
    """Получить статус по ID"""
    db_status = await crud.get_status(status_id=status_id)
    if db_status is None:
        raise HTTPException(status_code=404, detail="Статус не найден")
    return db_status


@router.post("/", response_model=schemas.Status, status_code=status.HTTP_201_CREATED)
async def create_status(
    status_data: schemas.StatusCreate,
    current_user = Depends(require_admin)
):
    """Создать новый статус (только для админов)"""
    return await crud.create_status(status=status_data)


@router.put("/{status_id}", response_model=schemas.Status)
async def update_status(
    status_id: int, 
    status_data: schemas.StatusUpdate,
    current_user = Depends(require_admin)
):
    """Обновить статус (только для админов)"""
    db_status = await crud.update_status(status_id=status_id, status=status_data)
    if db_status is None:
        raise HTTPException(status_code=404, detail="Статус не найден")
    return db_status


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status(
    status_id: int,
    current_user = Depends(require_admin)
):
    """Удалить статус (только для админов)"""
    db_status = await crud.delete_status(status_id=status_id)
    if db_status is None:
        raise HTTPException(status_code=404, detail="Статус не найден")
    return None
