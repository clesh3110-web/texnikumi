import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from apps.accounts.permissions import admin_required, student_required
from apps.groups.models import Group
from apps.students.models import StudentProfile
from .models import AttendanceDocument

@login_required
def documents_list_view(request):
    """
    Spravka va tushuntirish xatlarini tekshirish jurnali (Section 9.1).
    Admin va guruh rahbarlari yangi yuklangan hujjatlarni tekshirib tasdiqlaydi yoki rad etadi.
    """
    user = request.user
    if user.is_student:
        return redirect('documents:student_documents')

    # Filtrlar
    status_filter = request.GET.get('status', '')
    group_filter = request.GET.get('group', '')

    docs = AttendanceDocument.objects.select_related('student__user', 'group', 'reviewed_by').all()

    # O'qituvchi bo'lsa faqat o'zi kuratorlik qiladigan guruh hujjatlarini ko'radi
    if user.is_teacher and not user.is_superuser:
        docs = docs.filter(group__curator=user.teacher_profile)

    if status_filter:
        docs = docs.filter(status=status_filter)
    if group_filter:
        docs = docs.filter(group__name=group_filter)

    # Hujjatni tasdiqlash yoki rad etish (POST)
    if request.method == 'POST':
        doc_id = request.POST.get('doc_id')
        new_status = request.POST.get('status')
        review_comment = request.POST.get('review_comment', '').strip()

        if doc_id and new_status in [AttendanceDocument.Status.APPROVED, AttendanceDocument.Status.REJECTED]:
            document = get_object_or_404(AttendanceDocument, id=doc_id)
            if not document.can_user_access(user):
                raise PermissionDenied("Siz ushbu hujjatni tekshirish huquqiga ega emassiz!")

            document.status = new_status
            document.reviewed_by = user
            document.reviewed_at = timezone.now()
            document.review_comment = review_comment
            document.save()
            messages.success(request, f"{document.student.user.get_full_name_uz} hujjati {document.get_status_display().lower()} holatiga o‘tkazildi.")
            return redirect(request.get_full_path())

    context = {
        'documents': docs,
        'groups': Group.objects.all(),
        'status_filter': status_filter,
        'group_filter': group_filter,
        'statuses': AttendanceDocument.Status.choices,
    }
    return render(request, 'documents/documents_list.html', context)


@student_required
def student_upload_document_view(request):
    """
    O‘quvchi tomonidan tibbiy spravka yoki tushuntirish xatini yuklash (Section 9.1).
    """
    student = request.user.student_profile

    if request.method == 'POST':
        doc_type = request.POST.get('doc_type')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        reason = request.POST.get('reason', '').strip()
        uploaded_file = request.FILES.get('file')

        if doc_type and start_date_str and end_date_str and uploaded_file:
            try:
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

                if start_date > end_date:
                    messages.error(request, "Boshlanish sanasi tugash sanasidan katta bo‘lishi mumkin emas!")
                else:
                    doc = AttendanceDocument.objects.create(
                        student=student,
                        group=student.group,
                        doc_type=doc_type,
                        start_date=start_date,
                        end_date=end_date,
                        reason=reason,
                        file=uploaded_file,
                        status=AttendanceDocument.Status.NEW
                    )
                    messages.success(request, "Hujjatingiz muvaffaqiyatli yuklandi va tekshiruvga yuborildi.")
                    return redirect('documents:student_documents')
            except Exception as e:
                messages.error(request, f"Xatolik: {e}")
        else:
            messages.error(request, "Iltimos, barcha maydonlarni to‘ldiring va faylni tanlang.")

    my_documents = AttendanceDocument.objects.filter(student=student).order_by('-created_at')

    context = {
        'student': student,
        'my_documents': my_documents,
        'doc_types': AttendanceDocument.DocType.choices,
    }
    return render(request, 'documents/student_documents.html', context)


@login_required
def document_detail_view(request, doc_id):
    """
    Hujjatni ko'rish (Section 9.1).
    XAVFSIZLIK: Tibbiy hujjatlar maxfiy! Begona foydalanuvchilar kira olmaydi!
    """
    document = get_object_or_404(AttendanceDocument.objects.select_related('student__user', 'group', 'reviewed_by'), id=doc_id)

    if not document.can_user_access(request.user):
        raise PermissionDenied("Sizda ushbu maxfiy tibbiy hujjatni ko‘rish huquqi mavjud emas!")

    return render(request, 'documents/document_detail.html', {'document': document})
