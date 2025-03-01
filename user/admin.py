from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Branch

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'passport_number', 'user_status', 'role', 'branch', 'is_active')
    list_filter = ('user_status', 'role', 'branch')
    fieldsets = (
        (None, {'fields': ('passport_number', 'password')}),
        ('Personal info', {'fields': ('username', 'branch')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'user_status')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('passport_number', 'username', 'password', 'branch', 'role', 'user_status'),
        }),
    )
    search_fields = ('passport_number', 'username')
    ordering = ('username',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(Branch)