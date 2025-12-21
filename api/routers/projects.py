from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import crud
import schemas
from auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[schemas.Project])
async def read_projects(
    skip: int = 0, 
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Получить список всех проектов"""
    projects = await crud.get_projects(skip=skip, limit=limit)
    return projects


@router.get("/{project_id}", response_model=schemas.Project)
async def read_project(
    project_id: int,
    current_user = Depends(get_current_user)
):
    """Получить проект по ID"""
    db_project = await crud.get_project(project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return db_project


@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: schemas.ProjectCreate,
    current_user = Depends(get_current_user)
):
    """Создать новый проект"""
    return await crud.create_project(project=project, user_id=current_user.id)


@router.put("/{project_id}", response_model=schemas.Project)
async def update_project(
    project_id: int, 
    project: schemas.ProjectUpdate,
    current_user = Depends(get_current_user)
):
    """Обновить проект"""
    db_project = await crud.update_project(project_id=project_id, project=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user = Depends(get_current_user)
):
    """Удалить проект"""
    db_project = await crud.delete_project(project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return None
