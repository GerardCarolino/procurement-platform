from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'organization', 'is_active')
    list_filter = ('role', 'is_verified', 'is_active')
    list_editable = ('is_verified',)
    search_fields = ('username', 'email', 'organization')

    fieldsets = UserAdmin.fieldsets + (
        ('Procurement Profile', {
            'fields': ('role', 'is_verified', 'phone', 'organization')
        }),
    )