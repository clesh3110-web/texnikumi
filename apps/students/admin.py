from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'group',
        'student_id_number',
        'education_type',
        'status',
        'parent_phone',
    ]
    list_filter = ['group', 'education_type', 'status', 'enrollment_year']
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__phone',
        'student_id_number',
        'parent_name',
        'parent_phone',
    ]
    autocomplete_fields = ['group']
