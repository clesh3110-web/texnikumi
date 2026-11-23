from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username',
        'get_full_name_uz',
        'role',
        'phone',
        'email',
        'is_active',
        'date_joined',
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'gender', 'date_joined']
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'middle_name',
        'phone',
        'email',
        'jshshir',
    ]
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Shaxsiy ma‘lumotlar'), {
            'fields': (
                'first_name',
                'last_name',
                'middle_name',
                'role',
                'phone',
                'email',
                'jshshir',
                'avatar',
                'birth_date',
                'gender',
                'address',
            )
        }),
        (_('Huquqlar va Ruxsatlar'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Muhim sanalar'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'first_name',
                'last_name',
                'role',
                'phone',
                'password',
            ),
        }),
    )
