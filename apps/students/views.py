import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Avg, Count, Q
from apps.accounts.permissions import student_required
from apps.subjects.models import Subject, TeacherSubjectGroup
from apps.journal.models import Grade
from apps.attendance.models import Attendance
from apps.assignments.models import AssignmentSubmission
from .models import StudentProfile

@student_required
def student_dashboard_view(request):
    """
    O‘quvchi shaxsiy boshqaruv kabineti.
    Faqat o'ziga tegishli ma'lumotlar: baholar, davomat, dars jadvali va topshiriqlar.
    """
    student = request.user.student_profile
    group = student.group

    # Guruhga biriktirilgan fanlar va o'qituvchilar
    if group:
        assignments = group.teaching_assignments.select_related('teacher__user', 'subject').filter(is_active=True)
    else:
        assignments = []

    context = {
        'student': student,
        'group': group,
        'assignments': assignments,
        # Haqiqiy shaxsiy ko'rsatkichlar
        'gpa': student.gpa,
        'attendance_percentage': student.attendance_percentage,
        'activity_percentage': 0,
        'unread_notifications_count': 0,
    }
    return render(request, 'student/dashboard.html', context)


@student_required
def student_teachers_view(request):
    """
    O‘qituvchilarim bo‘limi (Section 12).
    O'quvchi o'z guruhiga dars beradigan barcha ustozlarni ko'radi.
    """
    student = request.user.student_profile
    group = student.group

    if group:
        assignments = group.teaching_assignments.select_related('teacher__user', 'subject').filter(is_active=True)
    else:
        assignments = []

    context = {
        'student': student,
        'group': group,
        'assignments': assignments,
    }
    return render(request, 'student/my_teachers.html', context)


@student_required
def student_analytics_view(request):
    """
    O‘quvchining shaxsiy akademik tahlili va Chart.js diagrammalari (Section 19).
    Fanlar kesimida o'zlashtirish, davomat taqsimoti, dinamika.
    """
    student = request.user.student_profile
    group = student.group

    # 1. Fanlar kesimidagi statistika
    subject_stats = []
    subject_labels = []
    subject_scores = []
    subject_attendances = []

    subjects = Subject.objects.filter(teaching_assignments__group=group, is_active=True).distinct()

    for subj in subjects:
        # O'rtacha baho
        avg_score = Grade.objects.filter(student=student, subject=subj).aggregate(Avg('score'))['score__avg']
        rounded_avg = round(avg_score, 2) if avg_score else 4.0

        # Davomat
        subj_att = Attendance.objects.filter(student=student, subject=subj)
        total_att = subj_att.count()
        if total_att > 0:
            present_att = subj_att.filter(status__in=[Attendance.Status.PRESENT, Attendance.Status.LATE]).count()
            att_rate = round((present_att / total_att) * 100, 1)
        else:
            att_rate = 0.0

        # Topshiriqlar
        subm_count = AssignmentSubmission.objects.filter(student=student, assignment__assignment__subject=subj).count()

        subject_stats.append({
            'subject': subj,
            'avg_score': rounded_avg,
            'attendance_rate': att_rate,
            'submissions_count': subm_count
        })

        subject_labels.append(subj.name)
        subject_scores.append(float(rounded_avg))
        subject_attendances.append(float(att_rate))

    # 2. Davomat taqsimoti (Donut Chart)
    all_att = Attendance.objects.filter(student=student)
    present_cnt = all_att.filter(status=Attendance.Status.PRESENT).count()
    late_cnt = all_att.filter(status=Attendance.Status.LATE).count()
    sick_cnt = all_att.filter(status=Attendance.Status.SICK).count()
    absent_cnt = all_att.filter(status=Attendance.Status.ABSENT).count()

    attendance_donut_data = [present_cnt, late_cnt, sick_cnt, absent_cnt]

    # 3. Oylik GPA o'zgarishi (Line Chart)
    monthly_labels = []
    monthly_gpa = []

    context = {
        'student': student,
        'group': group,
        'subject_stats': subject_stats,
        'subject_labels_json': json.dumps(subject_labels),
        'subject_scores_json': json.dumps(subject_scores),
        'subject_attendances_json': json.dumps(subject_attendances),
        'attendance_donut_json': json.dumps(attendance_donut_data),
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_gpa_json': json.dumps(monthly_gpa),
        'gpa': student.gpa,
        'attendance_percentage': student.attendance_percentage,
    }
    return render(request, 'student/analytics.html', context)
