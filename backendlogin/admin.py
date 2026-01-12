from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BackendCustomUser
class CustomUserAdmin(UserAdmin):
    model = BackendCustomUser
    list_display = ['username', 'email', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('is_influencer','full_name', 'dob', 'address', 'mobile')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
admin.site.register(BackendCustomUser, CustomUserAdmin)
# Register your models here.
