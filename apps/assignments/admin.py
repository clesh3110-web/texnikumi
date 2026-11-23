from django.contrib import admin
from .models import Assignment, AssignmentSubmission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_group', 'get_subject', 'due_date', 'max_score', 'created_by']
    list_filter = ['assignment__group', 'assignment__subject', 'due_date']
    search_fields = ['title', 'topic', 'description']
    autocomplete_fields = ['assignment']

    def get_group(self, obj):
        return obj.assignment.group.name
    get_group.short_description = "Guruh"

    def get_subject(self, obj):
        return obj.assignment.subject.name
    get_subject.short_description = "Fan"

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'status', 'score', 'submitted_at', 'graded_at']
    list_filter = ['status', 'score', 'submitted_at']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'assignment__title']
    autocomplete_fields = ['assignment', 'student']
