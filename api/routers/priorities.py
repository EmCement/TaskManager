from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import crud
import schemas
from auth import get_current_user, require_admin

router = APIRouter(prefix="/priorities", tags=["priorities"])


@router.get("/", response_model=List[schemas.Priority])
async def read_priorities(current_user = Depends(get_current_user)):
    """Получить список всех приоритетов"""
    priorities = await crud.get_priorities()
    return priorities


@router.get("/{priority_id}", response_model=schemas.Priority)
async def read_priority(
    priority_id: int,
    current_user = Depends(get_current_user)
):
    """Получить приоритет по ID"""
    db_priority = await crud.get_priority(priority_id=priority_id)
    if db_priority is None:
        raise HTTPException(status_code=404, detail="Приоритет не найден")
    return db_priority


@router.post("/", response_model=schemas.Priority, status_code=status.HTTP_201_CREATED)
async def create_priority(
    priority: schemas.PriorityCreate,
    current_user = Depends(require_admin)
):
    """Создать новый приоритет (только для админов)"""
    return await crud.create_priority(priority=priority)


@router.put("/{priority_id}", response_model=schemas.Priority)
async def update_priority(
    priority_id: int, 
    priority: schemas.PriorityUpdate,
    current_user = Depends(require_admin)
):
    """Обновить приоритет (только для админов)"""
    db_priority = await crud.update_priority(priority_id=priority_id, priority=priority)
    if db_priority is None:
        raise HTTPException(status_code=404, detail="Приоритет не найден")
    return db_priority


@router.delete("/{priority_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_priority(
    priority_id: int,
    current_user = Depends(require_admin)
):
    """Удалить приоритет (только для админов)"""
    db_priority = await crud.delete_priority(priority_id=priority_id)
    if db_priority is None:
        raise HTTPException(status_code=404, detail="Приоритет не найден")
    return None
