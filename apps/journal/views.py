import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from apps.groups.models import Group
from apps.subjects.models import Subject, TeacherSubjectGroup
from apps.students.models import StudentProfile
from .models import Grade, GradeAuditLog

@login_required
def journal_view(request):
    """
    Elektron Jurnal interfeysi (Section 8).
    Guruh va fanni tanlab, 5 ballik baholash jadvalini ko'rish va baho qo'yish.
    """
    user = request.user
    
    # O'qituvchi bo'lsa faqat o'z biriktiruvlari, Admin bo'lsa barchasi
    if user.is_teacher:
        assignments = user.teacher_profile.teaching_assignments.select_related('group', 'subject').filter(is_active=True)
    elif user.is_admin_user:
        assignments = TeacherSubjectGroup.objects.select_related('group', 'subject', 'teacher__user').filter(is_active=True)
    elif user.is_student:
        return redirect('journal:student_grades')
    else:
        assignments = TeacherSubjectGroup.objects.none()

    selected_assignment_id = request.GET.get('assignment')
    selected_assignment = None
    students = []
    grades_dict = {}

    if selected_assignment_id:
        selected_assignment = get_object_or_404(TeacherSubjectGroup, id=selected_assignment_id)
        
        # Xavfsizlik: O'qituvchi boshqa o'qituvchining darsiga baho qo'ya olmaydi!
        if user.is_teacher and selected_assignment.teacher != user.teacher_profile and not user.is_superuser:
            raise PermissionDenied("Siz ushbu fanga biriktirilmagansiz!")

        students = selected_assignment.group.students.select_related('user').filter(status='ACTIVE')
        
        # Baholarni olish
        grades = Grade.objects.filter(assignment=selected_assignment).select_related('student')
        for g in grades:
            key = f"{g.student_id}_{g.lesson_date.strftime('%Y-%m-%d')}"
            grades_dict[key] = g

    # Baho qo'yish yoki tahrirlash (POST so'rov)
    if request.method == 'POST' and selected_assignment:
        student_id = request.POST.get('student_id')
        lesson_date_str = request.POST.get('lesson_date')
        score = request.POST.get('score')
        grade_type = request.POST.get('grade_type', Grade.GradeType.CURRENT)
        comment = request.POST.get('comment', '').strip()
        audit_reason = request.POST.get('audit_reason', '').strip()

        if student_id and lesson_date_str and score:
            student = get_object_or_404(StudentProfile, id=student_id)
            lesson_date = datetime.datetime.strptime(lesson_date_str, '%Y-%m-%d').date()
            score_int = int(score)

            # Mavjud bahoni tekshirish
            existing_grade = Grade.objects.filter(
                student=student,
                assignment=selected_assignment,
                lesson_date=lesson_date
            ).first()

            if existing_grade:
                old_score = existing_grade.score
                if old_score != score_int:
                    # Baho o'zgarsa Audit tarixiga yozish (Section 8 & 24)
                    GradeAuditLog.objects.create(
                        grade=existing_grade,
                        student_name=student.user.get_full_name_uz,
                        subject_name=selected_assignment.subject.name,
                        old_score=old_score,
                        new_score=score_int,
                        changed_by=user,
                        reason=audit_reason or "O‘qituvchi tomonidan qayta baholandi"
                    )
                existing_grade.score = score_int
                existing_grade.grade_type = grade_type
                existing_grade.comment = comment
                existing_grade.save()
                messages.success(request, f"{student.user.get_full_name_uz} uchun baho muvaffaqiyatli yangilandi!")
            else:
                new_grade = Grade.objects.create(
                    student=student,
                    assignment=selected_assignment,
                    lesson_date=lesson_date,
                    score=score_int,
                    grade_type=grade_type,
                    comment=comment,
                    created_by=user
                )
                messages.success(request, f"{student.user.get_full_name_uz} uchun {score_int} ball qo‘yildi!")

            return redirect(f"{request.path}?assignment={selected_assignment.id}")

    context = {
        'assignments': assignments,
        'selected_assignment': selected_assignment,
        'students': students,
        'grades_dict': grades_dict,
        'today': datetime.date.today(),
    }
    return render(request, 'journal/journal_view.html', context)


@login_required
def student_grades_view(request):
    """O'quvchi uchun o'zining barcha fanlar bo'yicha baholari (Section 4.4 & 10)"""
    if not hasattr(request.user, 'student_profile'):
        return redirect('accounts:dashboard_redirect')

    student = request.user.student_profile
    grades = Grade.objects.filter(student=student).select_related('assignment__subject', 'created_by')

    # Fanlar bo'yicha guruhlash
    subjects_grades = {}
    for g in grades:
        subj = g.assignment.subject.name
        if subj not in subjects_grades:
            subjects_grades[subj] = []
        subjects_grades[subj].append(g)

    context = {
        'student': student,
        'subjects_grades': subjects_grades,
        'grades': grades,
    }
    return render(request, 'journal/student_grades.html', context)
