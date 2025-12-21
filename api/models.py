from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=100, null=True)
    role = fields.CharField(max_length=20, default='user')
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "user"

    def __str__(self):
        return self.username


class Project(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    created_by = fields.ForeignKeyField('models.User', related_name='created_projects', null=True, on_delete=fields.SET_NULL)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "project"

    def __str__(self):
        return self.name


class Priority(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=20, unique=True)
    level = fields.IntField()
    color = fields.CharField(max_length=7, default='#6B7280')

    class Meta:
        table = "priority"

    def __str__(self):
        return self.name


class Status(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=30, unique=True)
    order_num = fields.IntField(default=0)
    is_final = fields.BooleanField(default=False)

    class Meta:
        table = "status"

    def __str__(self):
        return self.name


class Task(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    description = fields.TextField(null=True)
    project = fields.ForeignKeyField('models.Project', related_name='tasks', on_delete=fields.CASCADE)
    priority = fields.ForeignKeyField('models.Priority', related_name='tasks', null=True, on_delete=fields.SET_NULL)
    status = fields.ForeignKeyField('models.Status', related_name='tasks', null=True, on_delete=fields.SET_NULL)
    created_by = fields.ForeignKeyField('models.User', related_name='created_tasks', null=True, on_delete=fields.SET_NULL)
    due_date = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    assignees = fields.ManyToManyField('models.User', related_name='assigned_tasks', through='task_assignee')

    class Meta:
        table = "task"

    def __str__(self):
        return self.title


class Comment(Model):
    id = fields.IntField(pk=True)
    task = fields.ForeignKeyField('models.Task', related_name='comments', on_delete=fields.CASCADE)
    user = fields.ForeignKeyField('models.User', related_name='comments', null=True, on_delete=fields.SET_NULL)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "comment"


class Attachment(Model):
    id = fields.IntField(pk=True)
    task = fields.ForeignKeyField('models.Task', related_name='attachments', on_delete=fields.CASCADE)
    user = fields.ForeignKeyField('models.User', related_name='attachments', null=True, on_delete=fields.SET_NULL)
    filename = fields.CharField(max_length=255)
    filepath = fields.CharField(max_length=500)
    size = fields.BigIntField(null=True)
    mime_type = fields.CharField(max_length=100, null=True)
    uploaded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "attachment"
