from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.subjects.models import Subject
from .models import Book, BookRequest

def library_catalog_view(request):
    """Elektron kutubxona katalogi va qidiruv (Section 18)"""
    query = request.GET.get('q', '').strip()
    subject_id = request.GET.get('subject', '')

    books = Book.objects.filter(is_public=True).select_related('subject')

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query) |
            Q(isbn__icontains=query)
        )
    if subject_id:
        books = books.filter(subject_id=subject_id)

    subjects = Subject.objects.filter(is_active=True)

    context = {
        'books': books,
        'subjects': subjects,
        'query': query,
        'selected_subject_id': int(subject_id) if subject_id.isdigit() else None,
        'total_books_count': books.count(),
    }
    return render(request, 'library/catalog.html', context)


def book_detail_view(request, book_id):
    """Kitob tafsilotlari va PDF mutolaa qilish"""
    book = get_object_or_404(Book, id=book_id, is_public=True)
    
    # Ko'rishlar sonini oshirish
    Book.objects.filter(id=book.id).update(views_count=F('views_count') + 1)
    book.refresh_from_db()

    # Yuklab olish so'rovi bo'lsa
    if request.GET.get('download') == '1':
        Book.objects.filter(id=book.id).update(downloads_count=F('downloads_count') + 1)
        return redirect(book.pdf_file.url)

    related_books = Book.objects.filter(subject=book.subject, is_public=True).exclude(id=book.id)[:3]

    context = {
        'book': book,
        'related_books': related_books,
    }
    return render(request, 'library/book_detail.html', context)
