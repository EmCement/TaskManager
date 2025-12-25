from typing import List, Optional
from tortoise.exceptions import DoesNotExist
import models
import schemas
from auth import get_password_hash


async def get_user(user_id: int):
    try:
        return await models.User.get(id=user_id)
    except DoesNotExist:
        return None


async def get_user_by_username(username: str):
    try:
        return await models.User.get(username=username)
    except DoesNotExist:
        return None


async def get_user_by_email(email: str):
    try:
        return await models.User.get(email=email)
    except DoesNotExist:
        return None


async def get_users(skip: int = 0, limit: int = 100):
    return await models.User.all().offset(skip).limit(limit)


async def create_user(user: schemas.UserCreate):
    user_data = user.model_dump(exclude={'password'})
    user_data['password_hash'] = get_password_hash(user.password)
    user_obj = await models.User.create(**user_data)
    return user_obj


async def update_user(user_id: int, user: schemas.UserUpdate):
    user_obj = await get_user(user_id)
    if user_obj:
        update_data = user.model_dump(exclude_unset=True, exclude={'password'})

        # Если передан новый пароль, хешируем его
        if user.password:
            update_data['password_hash'] = get_password_hash(user.password)

        await user_obj.update_from_dict(update_data)
        await user_obj.save()
    return user_obj


async def delete_user(user_id: int):
    user_obj = await get_user(user_id)
    if user_obj:
        await user_obj.delete()
    return user_obj


async def get_project(project_id: int, user_id: Optional[int] = None, user_role: Optional[str] = None):
    """Получение проекта с проверкой доступа"""
    try:
        project = await models.Project.get(id=project_id)
        # Проверяем доступ: админ видит все, остальные только свои
        if user_role != "admin" and user_id and project.created_by_id != user_id:
            return None
        return project
    except DoesNotExist:
        return None


async def get_projects(skip: int = 0, limit: int = 100, user_id: Optional[int] = None, user_role: Optional[str] = None):
    """Получение проектов с фильтрацией по пользователю"""
    query = models.Project.all()
    # Обычные пользователи видят только свои проекты
    if user_role != "admin" and user_id:
        query = query.filter(created_by_id=user_id)
    return await query.offset(skip).limit(limit)


async def create_project(project: schemas.ProjectCreate, user_id: int):
    project_data = project.model_dump()
    project_data['created_by_id'] = user_id
    project_obj = await models.Project.create(**project_data)
    return project_obj


async def update_project(project_id: int, project: schemas.ProjectUpdate, user_id: Optional[int] = None,
                         user_role: Optional[str] = None):
    """Обновление проекта с проверкой доступа"""
    project_obj = await get_project(project_id, user_id, user_role)
    if project_obj:
        await project_obj.update_from_dict(project.model_dump(exclude_unset=True))
        await project_obj.save()
    return project_obj


async def delete_project(project_id: int, user_id: Optional[int] = None, user_role: Optional[str] = None):
    """Удаление проекта с проверкой доступа"""
    project_obj = await get_project(project_id, user_id, user_role)
    if project_obj:
        await project_obj.delete()
    return project_obj


async def get_priority(priority_id: int):
    try:
        return await models.Priority.get(id=priority_id)
    except DoesNotExist:
        return None


async def get_priorities():
    return await models.Priority.all().order_by('level')


async def create_priority(priority: schemas.PriorityCreate):
    priority_obj = await models.Priority.create(**priority.model_dump())
    return priority_obj


async def update_priority(priority_id: int, priority: schemas.PriorityUpdate):
    priority_obj = await get_priority(priority_id)
    if priority_obj:
        await priority_obj.update_from_dict(priority.model_dump(exclude_unset=True))
        await priority_obj.save()
    return priority_obj


async def delete_priority(priority_id: int):
    priority_obj = await get_priority(priority_id)
    if priority_obj:
        await priority_obj.delete()
    return priority_obj


async def get_status(status_id: int):
    try:
        return await models.Status.get(id=status_id)
    except DoesNotExist:
        return None


async def get_statuses():
    return await models.Status.all().order_by('order_num')


async def create_status(status: schemas.StatusCreate):
    status_obj = await models.Status.create(**status.model_dump())
    return status_obj


async def update_status(status_id: int, status: schemas.StatusUpdate):
    status_obj = await get_status(status_id)
    if status_obj:
        await status_obj.update_from_dict(status.model_dump(exclude_unset=True))
        await status_obj.save()
    return status_obj


async def delete_status(status_id: int):
    status_obj = await get_status(status_id)
    if status_obj:
        await status_obj.delete()
    return status_obj


async def get_task(task_id: int, user_id: Optional[int] = None, user_role: Optional[str] = None):
    """Получение задачи с проверкой доступа"""
    try:
        task = await models.Task.get(id=task_id).prefetch_related('priority', 'status', 'project', 'assignees')

        # Проверяем доступ
        if user_role != "admin" and user_id:
            # Пользователь может видеть задачу если:
            # 1. Он создатель проекта
            # 2. Он создатель задачи
            # 3. Он назначен на задачу
            project = await task.project
            assignee_ids = [assignee.id for assignee in await task.assignees.all()]

            if (project.created_by_id != user_id and
                    task.created_by_id != user_id and
                    user_id not in assignee_ids):
                return None

        return task
    except DoesNotExist:
        return None


async def get_tasks(skip: int = 0, limit: int = 100, project_id: Optional[int] = None,
                    status_id: Optional[int] = None, priority_id: Optional[int] = None,
                    user_id: Optional[int] = None, user_role: Optional[str] = None):
    """Получение задач с фильтрацией по пользователю"""
    query = models.Task.all().prefetch_related('priority', 'status', 'project', 'assignees')

    # Фильтрация для обычных пользователей
    if user_role != "admin" and user_id:
        # Получаем ID проектов пользователя
        user_projects = await models.Project.filter(created_by_id=user_id).values_list('id', flat=True)

        # Получаем задачи где пользователь назначен
        from tortoise.expressions import Q
        query = query.filter(
            Q(project_id__in=user_projects) |  # Задачи из его проектов
            Q(created_by_id=user_id) |  # Задачи которые он создал
            Q(assignees__id=user_id)  # Задачи на которые он назначен
        ).distinct()

    if project_id:
        query = query.filter(project_id=project_id)
    if status_id:
        query = query.filter(status_id=status_id)
    if priority_id:
        query = query.filter(priority_id=priority_id)

    return await query.offset(skip).limit(limit)


async def create_task(task: schemas.TaskCreate, user_id: int):
    task_data = task.model_dump(exclude={'assignee_ids'})
    task_data['created_by_id'] = user_id
    task_obj = await models.Task.create(**task_data)

    if task.assignee_ids:
        assignees = await models.User.filter(id__in=task.assignee_ids)
        await task_obj.assignees.add(*assignees)

    return task_obj


async def update_task(task_id: int, task: schemas.TaskUpdate, user_id: Optional[int] = None,
                      user_role: Optional[str] = None):
    """Обновление задачи с проверкой доступа"""
    task_obj = await get_task(task_id, user_id, user_role)
    if task_obj:
        update_data = task.model_dump(exclude_unset=True, exclude={'assignee_ids'})
        await task_obj.update_from_dict(update_data)
        await task_obj.save()

        if task.assignee_ids is not None:
            await task_obj.assignees.clear()
            if task.assignee_ids:
                assignees = await models.User.filter(id__in=task.assignee_ids)
                await task_obj.assignees.add(*assignees)

    return task_obj


async def delete_task(task_id: int, user_id: Optional[int] = None, user_role: Optional[str] = None):
    """Удаление задачи с проверкой доступа"""
    task_obj = await get_task(task_id, user_id, user_role)
    if task_obj:
        await task_obj.delete()
    return task_obj


async def get_comment(comment_id: int):
    try:
        return await models.Comment.get(id=comment_id).prefetch_related('user')
    except DoesNotExist:
        return None


async def get_comments_by_task(task_id: int):
    return await models.Comment.filter(task_id=task_id).prefetch_related('user').all()


async def create_comment(comment: schemas.CommentCreate, user_id: int):
    comment_data = comment.model_dump()
    comment_data['user_id'] = user_id
    comment_obj = await models.Comment.create(**comment_data)
    return comment_obj


async def update_comment(comment_id: int, comment: schemas.CommentUpdate):
    comment_obj = await get_comment(comment_id)
    if comment_obj:
        await comment_obj.update_from_dict(comment.model_dump(exclude_unset=True))
        await comment_obj.save()
    return comment_obj


async def delete_comment(comment_id: int):
    comment_obj = await get_comment(comment_id)
    if comment_obj:
        await comment_obj.delete()
    return comment_obj


async def get_attachment(attachment_id: int):
    try:
        return await models.Attachment.get(id=attachment_id).prefetch_related('user')
    except DoesNotExist:
        return None


async def get_attachments_by_task(task_id: int):
    return await models.Attachment.filter(task_id=task_id).prefetch_related('user').all()


async def create_attachment(attachment: schemas.AttachmentCreate, user_id: int):
    attachment_data = attachment.model_dump()
    attachment_data['user_id'] = user_id
    attachment_obj = await models.Attachment.create(**attachment_data)
    return attachment_obj


async def delete_attachment(attachment_id: int):
    attachment_obj = await get_attachment(attachment_id)
    if attachment_obj:
        await attachment_obj.delete()
    return attachment_obj
