from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['date', 'lesson_pair', 'student', 'group', 'status', 'marked_by']
    list_filter = ['status', 'date', 'group', 'lesson_pair']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'group__name']
    autocomplete_fields = ['student', 'group', 'assignment']
