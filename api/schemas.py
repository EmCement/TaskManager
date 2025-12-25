from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = 'user'


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: str = 'user'


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Project(ProjectBase):
    id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PriorityBase(BaseModel):
    name: str
    level: int
    color: str = '#6B7280'


class PriorityCreate(PriorityBase):
    pass


class PriorityUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    color: Optional[str] = None


class Priority(PriorityBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class StatusBase(BaseModel):
    name: str
    order_num: int = 0
    is_final: bool = False


class StatusCreate(StatusBase):
    pass


class StatusUpdate(BaseModel):
    name: Optional[str] = None
    order_num: Optional[int] = None
    is_final: Optional[bool] = None


class Status(StatusBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    project_id: int
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    due_date: Optional[datetime] = None
    assignee_ids: Optional[List[int]] = None


class Task(TaskBase):
    id: int
    project_id: int
    priority_id: Optional[int] = None
    status_id: Optional[int] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskWithDetails(Task):
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    project: Optional[Project] = None
    assignees: List[User] = []

    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    task_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class Comment(CommentBase):
    id: int
    task_id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttachmentBase(BaseModel):
    filename: str
    filepath: str
    size: Optional[int] = None
    mime_type: Optional[str] = None


class AttachmentCreate(AttachmentBase):
    task_id: int


class Attachment(AttachmentBase):
    id: int
    task_id: int
    user_id: Optional[int] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentWithUser(Comment):
    user: Optional[User] = None

    model_config = ConfigDict(from_attributes=True)


class AttachmentWithUser(Attachment):
    user: Optional[User] = None

    model_config = ConfigDict(from_attributes=True)
