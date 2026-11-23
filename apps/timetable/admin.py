from django.contrib import admin
from .models import TimetableItem

@admin.register(TimetableItem)
class TimetableItemAdmin(admin.ModelAdmin):
    list_display = ['group', 'weekday', 'lesson_pair', 'get_subject', 'get_teacher', 'room', 'start_time', 'end_time']
    list_filter = ['weekday', 'group', 'academic_year', 'semester']
    search_fields = ['group__name', 'assignment__subject__name', 'assignment__teacher__user__first_name', 'room']
    autocomplete_fields = ['group', 'assignment']

    def get_subject(self, obj):
        return obj.assignment.subject.name
    get_subject.short_description = "Fan"

    def get_teacher(self, obj):
        return obj.assignment.teacher.user.get_full_name_uz
    get_teacher.short_description = "O‘qituvchi"
