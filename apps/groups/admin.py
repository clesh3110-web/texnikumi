from django.contrib import admin
from .models import Group

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'direction', 'curator', 'academic_year', 'total_students_count', 'is_active']
    list_filter = ['course', 'academic_year', 'is_active', 'direction']
    search_fields = ['name', 'direction', 'curator__user__first_name', 'curator__user__last_name']
    autocomplete_fields = ['curator']
