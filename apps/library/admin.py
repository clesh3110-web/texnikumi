from django.contrib import admin
from .models import Book, BookRequest

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'subject', 'published_year', 'views_count', 'downloads_count', 'is_public']
    list_filter = ['subject', 'is_public', 'published_year']
    search_fields = ['title', 'author', 'isbn', 'description']
    autocomplete_fields = ['subject']

@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at', 'subject']
    search_fields = ['student__user__first_name', 'student__user__last_name', 'subject__name', 'comment']
    autocomplete_fields = ['student', 'subject']
