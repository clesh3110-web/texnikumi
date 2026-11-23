from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.groups.models import Group
from apps.subjects.models import Subject
from apps.library.models import Book, BookRequest
from .models import TimetableItem

@login_required
def timetable_view(request):
    """
    Haftalik dars jadvali interfeysi (Section 17).
    O'quvchi va o'qituvchilar o'z jadvalini ko'radi.
    """
    user = request.user
    selected_group = None

    if user.is_student:
        selected_group = user.student_profile.group
        groups = [selected_group] if selected_group else []
    elif user.is_teacher:
        groups = list({a.group for a in user.teacher_profile.teaching_assignments.filter(is_active=True)})
        group_id = request.GET.get('group')
        selected_group = get_object_or_404(Group, id=group_id) if group_id else (groups[0] if groups else None)
    else: # Admin
        groups = Group.objects.filter(is_active=True)
        group_id = request.GET.get('group')
        selected_group = get_object_or_404(Group, id=group_id) if group_id else (groups.first() if groups.exists() else None)

    # 6 kunlik va 6 juftlik matritsasi
    timetable_matrix = {day_num: {} for day_num in range(1, 7)}

    if selected_group:
        items = TimetableItem.objects.filter(
            group=selected_group
        ).select_related('assignment__subject', 'assignment__teacher__user')

        for it in items:
            timetable_matrix[it.weekday][it.lesson_pair] = it

    weekdays = [
        (1, 'Dushanba'),
        (2, 'Seshanba'),
        (3, 'Chorshanba'),
        (4, 'Payshanba'),
        (5, 'Juma'),
        (6, 'Shanba'),
    ]

    context = {
        'groups': groups,
        'selected_group': selected_group,
        'timetable_matrix': timetable_matrix,
        'weekdays': weekdays,
        'pairs': TimetableItem.LESSON_PAIRS,
    }
    return render(request, 'timetable/timetable_view.html', context)


@login_required
def timetable_book_action_view(request, item_id):
    """
    Section 17: Dars jadvalidagi fan nomini bosganda tegishli elektron kitob ochilsin.
    Agar kitob mavjud bo'lmasa: 'Bu fan uchun elektron kitob hali yuklanmagan' xabari va so'rov yuborish.
    """
    item = get_object_or_404(TimetableItem.objects.select_related('assignment__subject'), id=item_id)
    subject = item.assignment.subject

    book = Book.objects.filter(subject=subject, is_public=True).first()

    if book:
        # Kitob mavjud bo'lsa darhol kitob sahifasiga o'tadi
        messages.success(request, f"'{subject.name}' fani bo‘yicha elektron kitob ochildi.")
        return redirect('library:book_detail', book_id=book.id)
    else:
        # Kitob hali yuklanmagan bo'lsa xabar beriladi
        messages.warning(
            request,
            f"'{subject.name}' fani uchun elektron kitob hali yuklanmagan. "
            "Quyidagi tugma orqali kitobni yuklash bo‘yicha kutubxonaga so‘rov yuborishingiz mumkin."
        )
        return redirect(f"{request.META.get('HTTP_REFERER', '/timetable/')}?missing_book_subject={subject.id}")


@login_required
def request_book_view(request, subject_id):
    """O'quvchi tomonidan kitob so'rovi yuborish (Section 17 & 18)"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if hasattr(request.user, 'student_profile'):
        BookRequest.objects.get_or_create(
            student=request.user.student_profile,
            subject=subject,
            defaults={'comment': f"{subject.name} fani bo‘yicha darslik kerak."}
        )
        messages.success(request, f"'{subject.name}' fani bo‘yicha kitob so‘rovingiz qabul qilindi. Tez orada kutubxonaga joylashtiriladi!")
    else:
        messages.info(request, "Kitob so‘rovi faqat o‘quvchilar tomonidan yuboriladi.")

    return redirect(request.META.get('HTTP_REFERER', '/timetable/'))
