from django.contrib import admin
from .models import Grade, GradeAuditLog

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'get_subject', 'score', 'grade_type', 'lesson_date', 'created_by']
    list_filter = ['grade_type', 'score', 'lesson_date', 'assignment__subject', 'assignment__group']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'assignment__subject__name', 'topic']
    autocomplete_fields = ['student', 'assignment']

    def get_subject(self, obj):
        return obj.assignment.subject.name
    get_subject.short_description = "Fan"

@admin.register(GradeAuditLog)
class GradeAuditLogAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'subject_name', 'old_score', 'new_score', 'changed_by', 'changed_at']
    list_filter = ['changed_at', 'new_score']
    search_fields = ['student_name', 'subject_name', 'changed_by__username']
    readonly_fields = ['grade', 'student_name', 'subject_name', 'old_score', 'new_score', 'changed_by', 'changed_at', 'reason']
