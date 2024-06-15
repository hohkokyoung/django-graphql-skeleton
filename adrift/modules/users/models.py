from django.db import models
from core.models import BaseModel
from .enums import Role as RoleEnum
from core.utils import safe_get

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser, BaseModel):
    email = models.EmailField(blank=False, max_length=254)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    class Meta:
        ordering = ["username"]

    # def has_roles(self, roles):
    #     return self.roles.filter(name__in=roles).exists()

class UserRole(BaseModel):
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)

    class Meta:
        app_label = "users"


class RoleQuerySet(models.QuerySet):
    def exists_by_names(self, names):
        return self.filter(name__in=names).exists()
    

class RoleManager(models.Manager):
    def get_queryset(self):
        return RoleQuerySet(self.model, using=self._db)
    
    def exists_by_names(self, names):
        return self.get_queryset().exists_by_names(names)
    
    def contains_duplicates(self, name):
        return Role.objects.filter(name=name).exists()

    def create(self, name):
        role = Role(name=name)
        role.save()

class Role(BaseModel):
    name = models.CharField(
        max_length=30,
        choices=[(enum.name, enum.value) for enum in RoleEnum],
        unique=True
    )
    users = models.ManyToManyField(User, related_name="roles", through=UserRole, through_fields=("role", "user"))

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    objects = RoleManager()
