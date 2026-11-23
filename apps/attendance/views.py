import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.groups.models import Group
from apps.students.models import StudentProfile
from apps.documents.models import AttendanceDocument
from .models import Attendance

@login_required
def attendance_view(request):
    """
    Elektron Davomat kiritish va monitoring sahifasi (Section 9 & 9.1).
    Guruh, sana va juftlikni tanlab, o'quvchilarni belgilash.
    """
    user = request.user
    
    if user.is_teacher:
        groups = list({a.group for a in user.teacher_profile.teaching_assignments.filter(is_active=True)})
    elif user.is_admin_user:
        groups = Group.objects.filter(is_active=True)
    elif user.is_student:
        return redirect('attendance:student_attendance')
    else:
        groups = []

    group_id = request.GET.get('group')
    date_str = request.GET.get('date', datetime.date.today().strftime('%Y-%m-%d'))
    pair_str = request.GET.get('pair', '1')

    selected_group = None
    students_data = []
    
    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = datetime.date.today()

    pair_int = int(pair_str) if pair_str.isdigit() else 1

    if group_id:
        selected_group = get_object_or_404(Group, id=group_id)
        students = selected_group.students.select_related('user').filter(status='ACTIVE')

        # Ushbu kun va juftlikdagi mavjud davomat yozuvlari
        existing_records = {
            a.student_id: a for a in Attendance.objects.filter(
                group=selected_group,
                date=selected_date,
                lesson_pair=pair_int
            )
        }

        # Ushbu sanaga to'g'ri keladigan spravka va tushuntirish xatlari (Section 9.1)
        documents = {
            doc.student_id: doc for doc in AttendanceDocument.objects.filter(
                group=selected_group,
                start_date__lte=selected_date,
                end_date__gte=selected_date
            ).select_related('reviewed_by')
        }

        for st in students:
            rec = existing_records.get(st.id)
            current_status = rec.status if rec else Attendance.Status.PRESENT
            doc = documents.get(st.id)

            students_data.append({
                'student': st,
                'status': current_status,
                'comment': rec.comment if rec else '',
                'document': doc,
            })

    # Davomatni saqlash (POST so'rov)
    if request.method == 'POST' and selected_group:
        saved_count = 0
        for item in students_data:
            st = item['student']
            status_val = request.POST.get(f'status_{st.id}', Attendance.Status.PRESENT)
            comment_val = request.POST.get(f'comment_{st.id}', '').strip()

            attendance_obj, created = Attendance.objects.update_or_create(
                student=st,
                group=selected_group,
                date=selected_date,
                lesson_pair=pair_int,
                defaults={
                    'status': status_val,
                    'comment': comment_val,
                    'marked_by': user,
                }
            )
            saved_count += 1

        messages.success(request, f"{selected_group.name} guruhi uchun {selected_date} sanasi ({pair_int}-juftlik) davomati saqlandi!")
        return redirect(f"{request.path}?group={selected_group.id}&date={selected_date.strftime('%Y-%m-%d')}&pair={pair_int}")

    context = {
        'groups': groups,
        'selected_group': selected_group,
        'selected_date': selected_date,
        'selected_pair': pair_int,
        'pairs': Attendance.LESSON_PAIRS,
        'students_data': students_data,
        'statuses': Attendance.Status.choices,
    }
    return render(request, 'attendance/attendance_view.html', context)


@login_required
def student_attendance_view(request):
    """O'quvchi uchun shaxsiy davomat hisoboti (Section 9.1 & 10)"""
    if not hasattr(request.user, 'student_profile'):
        return redirect('accounts:dashboard_redirect')

    student = request.user.student_profile
    attendances = Attendance.objects.filter(student=student).order_by('-date', 'lesson_pair')

    # Statistika
    total = attendances.count()
    present_count = attendances.filter(status=Attendance.Status.PRESENT).count()
    late_count = attendances.filter(status=Attendance.Status.LATE).count()
    sick_count = attendances.filter(status=Attendance.Status.SICK).count()
    absent_count = attendances.filter(status=Attendance.Status.ABSENT).count()

    overall_percent = round(((present_count + late_count) / total * 100), 1) if total > 0 else 100.0

    context = {
        'student': student,
        'attendances': attendances,
        'total': total,
        'present_count': present_count,
        'late_count': late_count,
        'sick_count': sick_count,
        'absent_count': absent_count,
        'overall_percent': overall_percent,
    }
    return render(request, 'attendance/student_attendance.html', context)


@login_required
def group_students_status_api(request):
    """
    Kasal, kechikkan, darsda yoki sababsiz kelmaganlar ustiga bosganda
    o'sha o'quvchilar ro'yxati, spravkasi va holatini qaytaruvchi API.
    Agar spravkasi bo'lmasa -> sababsiz ko'rinadi.
    Agar spravkasi bo'lsa -> spravka havolasi bilan kasallik (sababli) ko'rinadi.
    """
    from django.http import JsonResponse

    group_id = request.GET.get('group_id')
    status_filter = request.GET.get('status', 'SICK').upper()

    if group_id:
        groups = Group.objects.filter(id=group_id)
        group_title = groups.first().name if groups.exists() else "Guruh"
    else:
        groups = Group.objects.filter(is_active=True)
        group_title = "Barcha guruhlar"

    # Oxirgi dars / bugungi davomat yozuvlari
    latest_date = Attendance.objects.order_by('-date').values_list('date', flat=True).first()
    if not latest_date:
        latest_date = datetime.date.today()

    attendances = Attendance.objects.filter(
        group__in=groups,
        date=latest_date,
        status=status_filter
    ).select_related('student__user', 'student__group')

    # Spravkalar
    documents = AttendanceDocument.objects.filter(
        group__in=groups,
        start_date__lte=latest_date,
        end_date__gte=latest_date
    ).select_related('student__user', 'student__group')

    doc_map = {d.student_id: d for d in documents}

    status_labels = {
        'PRESENT': "Darsda qatnashayotganlar",
        'LATE': "Darsga kechikkanlar",
        'SICK': "Kasallik sababli kelmaganlar (Spravka bilan)",
        'ABSENT': "Sababsiz kelmaganlar (Spravka yo‘q)",
    }

    results = []
    for att in attendances:
        st = att.student
        doc = doc_map.get(st.id)

        has_spravka = (doc is not None and doc.doc_type == AttendanceDocument.DocType.SPRAVKA)
        spravka_url = doc.file.url if (doc and doc.file) else ""
        spravka_status = doc.get_status_display() if doc else "Topshirilmagan"

        results.append({
            'student_id': st.id,
            'name': st.user.get_full_name_uz,
            'student_id_number': st.student_id_number or f"GT-{st.id:04d}",
            'group_name': st.group.name if st.group else "",
            'avatar': st.user.avatar.url if st.user.avatar else "",
            'status': att.get_status_display(),
            'status_code': att.status,
            'comment': att.comment or "",
            'has_spravka': has_spravka,
            'spravka_url': spravka_url,
            'spravka_status': spravka_status,
            'spravka_dates': f"{doc.start_date.strftime('%d.%m.%Y')} - {doc.end_date.strftime('%d.%m.%Y')}" if doc else "",
            'document_id': doc.id if doc else None,
        })

    # Agar ushbu sanada yozuvlar bo'lmasa, lekin talabalar orasida spravkalilar bo'lsa
    if not results and status_filter in ['SICK', 'ABSENT']:
        if status_filter == 'SICK':
            for doc in documents.filter(doc_type=AttendanceDocument.DocType.SPRAVKA):
                st = doc.student
                results.append({
                    'student_id': st.id,
                    'name': st.user.get_full_name_uz,
                    'student_id_number': st.student_id_number or f"GT-{st.id:04d}",
                    'group_name': st.group.name if st.group else "",
                    'avatar': st.user.avatar.url if st.user.avatar else "",
                    'status': "Kasallik sababli (Spravka mavjud)",
                    'status_code': 'SICK',
                    'comment': doc.comment or "Tibbiy ma'lumotnoma (095/h)",
                    'has_spravka': True,
                    'spravka_url': doc.file.url if doc.file else "",
                    'spravka_status': doc.get_status_display(),
                    'spravka_dates': f"{doc.start_date.strftime('%d.%m.%Y')} - {doc.end_date.strftime('%d.%m.%Y')}",
                    'document_id': doc.id,
                })

    return JsonResponse({
        'group_id': group_id or '',
        'group_name': group_title,
        'status_code': status_filter,
        'status_label': status_labels.get(status_filter, status_filter),
        'date': latest_date.strftime('%d.%m.%Y'),
        'count': len(results),
        'students': results,
    })
