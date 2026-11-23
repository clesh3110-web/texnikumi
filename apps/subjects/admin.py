from django.contrib import admin
from .models import Subject, TeacherSubjectGroup

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'total_hours', 'lecture_hours', 'practical_hours', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']

@admin.register(TeacherSubjectGroup)
class TeacherSubjectGroupAdmin(admin.ModelAdmin):
    list_display = ['group', 'subject', 'get_teacher', 'academic_year', 'semester', 'is_active']
    list_filter = ['academic_year', 'semester', 'is_active', 'group']
    search_fields = [
        'group__name',
        'subject__name',
        'subject__code',
        'teacher__user__first_name',
        'teacher__user__last_name',
    ]
    autocomplete_fields = ['teacher', 'subject', 'group']

    def get_teacher(self, obj):
        return obj.teacher.user.get_full_name_uz
    get_teacher.short_description = "O‘qituvchi"
