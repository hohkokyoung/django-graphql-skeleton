from django.contrib import admin
from users.models import User, Role, UserRole

# Register your models here.
@admin.register(User, Role, UserRole)
class UserAdmin(admin.ModelAdmin):
    pass