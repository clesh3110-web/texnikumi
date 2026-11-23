from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from apps.accounts.permissions import teacher_required
from apps.students.models import StudentProfile
from apps.groups.models import Group
from apps.subjects.models import Subject, TeacherSubjectGroup
from .models import TeacherProfile

@teacher_required
def teacher_dashboard_view(request):
    """
    O‘qituvchi boshqaruv kabineti.
    Faqat ushbu o'qituvchiga biriktirilgan guruhlar va fanlar ko'rsatiladi.
    """
    teacher = request.user.teacher_profile
    assignments = teacher.teaching_assignments.select_related('group', 'subject').filter(is_active=True)

    # Guruhlar va fanlar to'plami
    my_groups = list({a.group for a in assignments})
    my_subjects = list({a.subject for a in assignments})

    # Ushbu o'qituvchi o'qitadigan jami talabalar soni
    total_students_count = StudentProfile.objects.filter(group__in=my_groups, status='ACTIVE').distinct().count()

    # O'qituvchi kuratorlik qilayotgan guruhlar
    curated_groups = teacher.curated_groups.filter(is_active=True)

    context = {
        'teacher': teacher,
        'assignments': assignments,
        'my_groups': my_groups,
        'my_subjects': my_subjects,
        'total_groups_count': len(my_groups),
        'total_subjects_count': len(my_subjects),
        'total_students_count': total_students_count,
        'curated_groups': curated_groups,
        # Ma'lumotlar kiritilmaguncha statistikalar nol bo'ladi.
        'average_grade': 0,
        'attendance_rate': 0,
        'pending_assignments_count': 0,
        'unread_messages_count': 0,
    }
    return render(request, 'teacher/dashboard.html', context)


@teacher_required
def teacher_groups_view(request):
    """O'qituvchining 'Mening guruhlarim' sahifasi"""
    teacher = request.user.teacher_profile
    assignments = teacher.teaching_assignments.select_related('group', 'subject').filter(is_active=True)
    my_groups = list({a.group for a in assignments})

    context = {
        'teacher': teacher,
        'my_groups': my_groups,
        'assignments': assignments,
    }
    return render(request, 'teacher/groups_list.html', context)


@teacher_required
def teacher_group_detail_view(request, group_id):
    """
    O'qituvchi o'ziga biriktirilgan guruhni ko'rishi.
    XAVFSIZLIK: O'qituvchi o'ziga ruxsat berilmagan boshqa guruhga KIRA OLMAYDI!
    """
    teacher = request.user.teacher_profile
    group = get_object_or_404(Group, id=group_id)

    # Ruxsat tekshiruvi: O'qituvchi bu guruhda dars beradimi yoki kuratormi?
    has_permission = teacher.teaching_assignments.filter(group=group).exists() or group.curator == teacher

    if not has_permission and not request.user.is_superuser:
        messages.error(request, "Siz ushbu guruhga biriktirilmagansiz! Boshqa o‘qituvchining guruhlariga kirish taqiqlangan.")
        raise PermissionDenied("Ushbu guruh ma'lumotlariga kirish huquqingiz yo'q.")

    students = group.students.select_related('user').filter(status='ACTIVE')
    my_assignments_in_group = teacher.teaching_assignments.filter(group=group)

    context = {
        'teacher': teacher,
        'group': group,
        'students': students,
        'assignments': my_assignments_in_group,
        'is_curator': (group.curator == teacher),
    }
    return render(request, 'teacher/group_detail.html', context)


@teacher_required
def teacher_student_detail_view(request, student_id):
    """
    O'quvchi profili — O'qituvchi uchun (Section 14).
    Shaxsiy ma'lumotlar, baholar, davomat va faollik ko'rsatkichlari.
    """
    teacher = request.user.teacher_profile
    student = get_object_or_404(StudentProfile.objects.select_related('user', 'group'), id=student_id)

    # Ruxsat tekshiruvi: O'qituvchi bu talabaning guruhida dars berishi kerak
    if student.group:
        has_permission = teacher.teaching_assignments.filter(group=student.group).exists() or student.group.curator == teacher
    else:
        has_permission = False

    if not has_permission and not request.user.is_superuser:
        messages.error(request, "Ushbu o‘quvchining profiliga kirish huquqingiz yo‘q!")
        raise PermissionDenied("Siz bu o'quvchiga dars bermaysiz.")

    context = {
        'teacher': teacher,
        'student': student,
        'group': student.group,
        # Akademik ko'rsatkichlar faqat real baho va davomatdan olinadi.
        'gpa': 0,
        'attendance_percentage': 0,
        'strong_subjects': [],
        'attention_needed_subjects': [],
    }
    return render(request, 'teacher/student_detail.html', context)
