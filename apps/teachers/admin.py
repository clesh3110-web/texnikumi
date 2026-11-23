from django.contrib import admin
from .models import TeacherProfile

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'department', 'degree', 'office_room', 'get_phone']
    list_filter = ['department', 'degree']
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__phone',
        'department',
        'specialization',
    ]

    def get_full_name(self, obj):
        return obj.user.get_full_name_uz
    get_full_name.short_description = "O‘qituvchi F.I.Sh"

    def get_phone(self, obj):
        return obj.user.phone
    get_phone.short_description = "Telefon raqami"
