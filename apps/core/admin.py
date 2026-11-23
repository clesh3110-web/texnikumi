from django.contrib import admin
from .models import News, Announcement, Leadership, ContactMessage

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at', 'views_count', 'is_published']
    list_filter = ['is_published', 'published_at']
    search_fields = ['title', 'summary', 'content']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'is_urgent', 'is_active', 'created_at']
    list_filter = ['is_urgent', 'is_active']
    search_fields = ['title', 'description']

@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'phone', 'email', 'order']
    list_editable = ['order']
    search_fields = ['full_name', 'position']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['full_name', 'phone', 'email', 'subject', 'message']
