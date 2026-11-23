from django.contrib import admin
from .models import Event, EventParticipant

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'organizer', 'is_public', 'participants_count')
    list_filter = ('is_public', 'event_date')
    search_fields = ('title', 'description', 'location', 'organizer')


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registered_at')
    list_filter = ('event', 'registered_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'event__title')
