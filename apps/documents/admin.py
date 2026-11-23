from django.contrib import admin
from .models import AttendanceDocument

@admin.register(AttendanceDocument)
class AttendanceDocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'doc_type', 'start_date', 'end_date', 'status', 'reviewed_by']
    list_filter = ['status', 'doc_type', 'group', 'start_date']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'reason', 'review_comment']
    autocomplete_fields = ['student', 'group']
