from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import crud
import schemas
from auth import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/task/{task_id}", response_model=List[schemas.CommentWithUser])
async def read_comments_by_task(
    task_id: int,
    current_user=Depends(get_current_user)
):
    """Получить все комментарии по задаче"""
    if not await crud.get_task(task_id):
        raise HTTPException(status_code=404, detail="Задача не найдена")

    comments = await crud.get_comments_by_task(task_id=task_id)
    return comments


@router.get("/{comment_id}", response_model=schemas.Comment)
async def read_comment(
    comment_id: int,
    current_user = Depends(get_current_user)
):
    """Получить комментарий по ID"""
    db_comment = await crud.get_comment(comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    return db_comment


@router.post("/", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: schemas.CommentCreate,
    current_user = Depends(get_current_user)
):
    """Создать новый комментарий"""
    # Проверяем существование задачи
    if not await crud.get_task(comment.task_id):
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    return await crud.create_comment(comment=comment, user_id=current_user.id)


@router.put("/{comment_id}", response_model=schemas.Comment)
async def update_comment(
    comment_id: int, 
    comment: schemas.CommentUpdate,
    current_user = Depends(get_current_user)
):
    """Обновить комментарий (только свой)"""
    db_comment = await crud.get_comment(comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    
    # Проверяем, что пользователь редактирует свой комментарий
    if db_comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете редактировать только свои комментарии"
        )
    
    updated_comment = await crud.update_comment(comment_id=comment_id, comment=comment)
    return updated_comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user = Depends(get_current_user)
):
    """Удалить комментарий (только свой или админ может все)"""
    db_comment = await crud.get_comment(comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Комментарий не найден")
    
    # Проверяем, что пользователь удаляет свой комментарий
    if db_comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете удалять только свои комментарии"
        )
    
    await crud.delete_comment(comment_id=comment_id)
    return None
