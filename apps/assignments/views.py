import datetime
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from apps.subjects.models import TeacherSubjectGroup
from .models import Assignment, AssignmentSubmission

@login_required
def assignment_list_view(request):
    """Uy vazifalari ro'yxati (Section 16)"""
    user = request.user

    if user.is_teacher:
        assignments = Assignment.objects.filter(
            assignment__teacher=user.teacher_profile
        ).select_related('assignment__group', 'assignment__subject')
        is_teacher = True
    elif user.is_student:
        group = user.student_profile.group
        assignments = Assignment.objects.filter(
            assignment__group=group
        ).select_related('assignment__subject', 'created_by')
        is_teacher = False
    else: # Admin
        assignments = Assignment.objects.select_related('assignment__group', 'assignment__subject').all()
        is_teacher = True

    context = {
        'assignments': assignments,
        'is_teacher': is_teacher,
    }
    return render(request, 'assignments/assignment_list.html', context)


@login_required
def assignment_create_view(request):
    """O'qituvchi tomonidan yangi uy vazifasi topshirig'ini yaratish"""
    user = request.user
    if not user.is_teacher and not user.is_admin_user:
        raise PermissionDenied("Faqat o‘qituvchilar uy vazifasi yarata oladi!")

    if user.is_teacher:
        teaching_assignments = user.teacher_profile.teaching_assignments.filter(is_active=True).select_related('group', 'subject')
    else:
        teaching_assignments = TeacherSubjectGroup.objects.filter(is_active=True).select_related('group', 'subject')

    if request.method == 'POST':
        tsg_id = request.POST.get('assignment_id')
        title = request.POST.get('title', '').strip()
        topic = request.POST.get('topic', '').strip()
        description = request.POST.get('description', '').strip()
        due_date_str = request.POST.get('due_date')
        file = request.FILES.get('attachment_file')

        if tsg_id and title and due_date_str:
            tsg = get_object_or_404(TeacherSubjectGroup, id=tsg_id)
            parsed_dt = datetime.datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            due_date = timezone.make_aware(parsed_dt) if timezone.is_naive(parsed_dt) else parsed_dt
            
            task = Assignment.objects.create(
                assignment=tsg,
                title=title,
                topic=topic,
                description=description,
                attachment_file=file,
                due_date=due_date,
                created_by=user
            )
            messages.success(request, f"{tsg.group.name} guruhi uchun '{title}' topshirig‘i e‘lon qilindi!")
            return redirect('assignments:assignment_list')
        else:
            messages.error(request, "Iltimos, barcha majburiy maydonlarni to‘ldiring.")

    return render(request, 'assignments/assignment_create.html', {'teaching_assignments': teaching_assignments})


@login_required
def assignment_detail_view(request, task_id):
    """
    Topshiriq batafsil sahifasi.
    O'quvchi: yechim yuboradi, baho va izohni ko'radi.
    O'qituvchi: yuborilgan ishlarni tekshiradi va baholaydi.
    """
    task = get_object_or_404(Assignment.objects.select_related('assignment__group', 'assignment__subject', 'created_by'), id=task_id)
    user = request.user

    student_submission = None
    all_submissions = []

    if user.is_student:
        student = user.student_profile
        student_submission, _ = AssignmentSubmission.objects.get_or_create(
            assignment=task,
            student=student,
            defaults={'status': AssignmentSubmission.Status.NEW}
        )

        # O'quvchi yechim topshirishi (POST)
        if request.method == 'POST' and 'submit_solution' in request.POST:
            text = request.POST.get('submission_text', '').strip()
            file = request.FILES.get('submission_file')

            student_submission.submission_text = text
            if file:
                student_submission.submission_file = file
            student_submission.status = AssignmentSubmission.Status.SUBMITTED
            student_submission.submitted_at = timezone.now()
            student_submission.save()
            messages.success(request, "Topshiriq yechimi o‘qituvchiga muvaffaqiyatli yuborildi!")
            return redirect('assignments:assignment_detail', task_id=task.id)

    else: # O'qituvchi yoki Admin
        all_submissions = task.submissions.select_related('student__user').all()

        # O'qituvchi baho qo'yishi yoki qayta ishlashni so'rashi (POST)
        if request.method == 'POST' and 'grade_submission' in request.POST:
            sub_id = request.POST.get('submission_id')
            score = request.POST.get('score')
            feedback = request.POST.get('teacher_feedback', '').strip()
            action_type = request.POST.get('action_type', 'GRADED')

            submission = get_object_or_404(AssignmentSubmission, id=sub_id, assignment=task)
            if action_type == 'REVISE':
                submission.status = AssignmentSubmission.Status.REVISE
            else:
                submission.status = AssignmentSubmission.Status.GRADED
                if score and score.isdigit():
                    submission.score = int(score)
            
            submission.teacher_feedback = feedback
            submission.graded_at = timezone.now()
            submission.save()
            messages.success(request, f"{submission.student.user.get_full_name_uz} uchun baho/taqriz saqlandi!")
            return redirect('assignments:assignment_detail', task_id=task.id)

    context = {
        'task': task,
        'student_submission': student_submission,
        'all_submissions': all_submissions,
        'is_student': user.is_student,
    }
    return render(request, 'assignments/assignment_detail.html', context)
