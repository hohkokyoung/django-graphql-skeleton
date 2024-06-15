import uuid
from django.db import models
from django.conf import settings

class BaseModel(models.Model):
    class Meta:
        app_label = "base"
        abstract = True

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='%(class)s_created_by', on_delete=models.SET_NULL, db_column="created_by")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='%(class)s_updated_by', on_delete=models.SET_NULL, db_column="updated_by")