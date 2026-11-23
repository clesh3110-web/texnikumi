"""
URL configuration for GULISTON 1-SON TEXNIKUM platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('teacher/', include('apps.teachers.urls', namespace='teachers')),
    path('student/', include('apps.students.urls', namespace='students')),
    path('journal/', include('apps.journal.urls', namespace='journal')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('documents/', include('apps.documents.urls', namespace='documents')),
    path('timetable/', include('apps.timetable.urls', namespace='timetable')),
    path('assignments/', include('apps.assignments.urls', namespace='assignments')),
    path('library/', include('apps.library.urls', namespace='library')),
    path('messages/', include('apps.messaging.urls', namespace='messaging')),
    path('events/', include('apps.events.urls', namespace='events')),
    path('projects/', include('apps.projects.urls', namespace='projects')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('audit/', include('apps.audit.urls', namespace='audit')),
    path('', include('apps.core.urls', namespace='core')),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
