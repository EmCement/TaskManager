from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
import crud
import schemas
from auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=List[schemas.TaskWithDetails])
async def read_tasks(
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[int] = Query(None, description="Фильтр по ID проекта"),
        status_id: Optional[int] = Query(None, description="Фильтр по ID статуса"),
        priority_id: Optional[int] = Query(None, description="Фильтр по ID приоритета"),
        current_user=Depends(get_current_user)
):
    """Получить список задач (пользователи видят только свои/назначенные, админы - все)"""
    tasks = await crud.get_tasks(
        skip=skip,
        limit=limit,
        project_id=project_id,
        status_id=status_id,
        priority_id=priority_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    return tasks


@router.get("/{task_id}", response_model=schemas.TaskWithDetails)
async def read_task(
        task_id: int,
        current_user=Depends(get_current_user)
):
    """Получить задачу по ID (только с доступом или все для админа)"""
    db_task = await crud.get_task(
        task_id=task_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    if db_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")
    return db_task


@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
async def create_task(
        task: schemas.TaskCreate,
        current_user=Depends(get_current_user)
):
    """Создать новую задачу (только в своих проектах)"""
    # Проверяем существование проекта и доступ к нему
    db_project = await crud.get_project(
        task.project_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    if not db_project:
        raise HTTPException(status_code=404, detail="Проект не найден или нет доступа")

    # Проверяем существование приоритета (если указан)
    if task.priority_id and not await crud.get_priority(task.priority_id):
        raise HTTPException(status_code=404, detail="Приоритет не найден")

    # Проверяем существование статуса (если указан)
    if task.status_id and not await crud.get_status(task.status_id):
        raise HTTPException(status_code=404, detail="Статус не найден")

    return await crud.create_task(task=task, user_id=current_user.id)


@router.put("/{task_id}", response_model=schemas.Task)
async def update_task(
        task_id: int,
        task: schemas.TaskUpdate,
        current_user=Depends(get_current_user)
):
    """Обновить задачу (только с доступом или все для админа)"""
    # Проверяем существование задачи и доступ к ней
    db_task = await crud.get_task(
        task_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    if not db_task:
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")

    # Проверяем существование проекта (если указан)
    if task.project_id:
        db_project = await crud.get_project(
            task.project_id,
            user_id=current_user.id,
            user_role=current_user.role
        )
        if not db_project:
            raise HTTPException(status_code=404, detail="Проект не найден или нет доступа")

    # Проверяем существование приоритета (если указан)
    if task.priority_id and not await crud.get_priority(task.priority_id):
        raise HTTPException(status_code=404, detail="Приоритет не найден")

    # Проверяем существование статуса (если указан)
    if task.status_id and not await crud.get_status(task.status_id):
        raise HTTPException(status_code=404, detail="Статус не найден")

    updated_task = await crud.update_task(
        task_id=task_id,
        task=task,
        user_id=current_user.id,
        user_role=current_user.role
    )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        current_user=Depends(get_current_user)
):
    """Удалить задачу (только с доступом или все для админа)"""
    db_task = await crud.delete_task(
        task_id=task_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    if db_task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена или нет доступа")
    return None
