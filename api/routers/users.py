from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import crud
import schemas
from auth import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0, 
    limit: int = 100,
    current_user = Depends(require_admin)
):
    """Получить список всех пользователей (только для админов)"""
    users = await crud.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    current_user = Depends(get_current_user)
):
    """Получить пользователя по ID"""
    db_user = await crud.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    current_user = Depends(require_admin)
):
    """Создать нового пользователя (только для админов)"""
    # Проверяем уникальность username и email
    db_user = await crud.get_user_by_username(username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким username уже существует")
    
    db_user = await crud.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    return await crud.create_user(user=user)


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int, 
    user: schemas.UserUpdate,
    current_user = Depends(get_current_user)
):
    """Обновить пользователя (только себя или админ может всех)"""
    # Обычный пользователь может редактировать только себя
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа"
        )
    
    # Обычный пользователь не может изменить свою роль
    if current_user.role != "admin" and user.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете изменить свою роль"
        )
    
    db_user = await crud.update_user(user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user = Depends(require_admin)
):
    """Удалить пользователя (только для админов)"""
    db_user = await crud.delete_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return None
