from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from apps.teachers.models import TeacherProfile
from .models import Project, ProjectComment

def projects_list_view(request):
    """Barcha loyihalar va startaplar ro'yxati (Section 22)"""
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')

    projects = Project.objects.select_related('creator', 'group', 'mentor__user').all()

    if category:
        projects = projects.filter(category=category)
    if status:
        projects = projects.filter(status=status)

    context = {
        'projects': projects,
        'categories': Project.Category.choices,
        'statuses': Project.Status.choices,
        'selected_category': category,
        'selected_status': status,
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_create_view(request):
    """Yangi startap / loyiha taklifini yuborish"""
    mentors = TeacherProfile.objects.select_related('user').all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', Project.Category.IT)
        description = request.POST.get('description', '').strip()
        mentor_id = request.POST.get('mentor_id')
        project_url = request.POST.get('project_url', '').strip()
        file = request.FILES.get('presentation_file')

        if not title or not description:
            messages.error(request, "Iltimos, loyiha nomi va tavsifini to‘ldiring.")
        else:
            group = None
            if hasattr(request.user, 'student_profile') and request.user.student_profile.group:
                group = request.user.student_profile.group

            mentor = TeacherProfile.objects.filter(id=mentor_id).first() if mentor_id else None

            project = Project.objects.create(
                title=title,
                creator=request.user,
                group=group,
                mentor=mentor,
                category=category,
                description=description,
                project_url=project_url,
                presentation_file=file,
                status=Project.Status.REVIEW
            )
            messages.success(request, f"'{project.title}' loyihasi ko‘rib chiqish uchun muvaffaqiyatli topshirildi!")
            return redirect('projects:project_detail', project_id=project.id)

    context = {
        'mentors': mentors,
        'categories': Project.Category.choices,
    }
    return render(request, 'projects/project_create.html', context)


def project_detail_view(request, project_id):
    """Loyiha tafsilotlari, taqdimot va muhokama fikrlari"""
    project = get_object_or_404(
        Project.objects.select_related('creator', 'group', 'mentor__user'),
        id=project_id
    )

    # Yangi fikr qoldirish (POST)
    if request.method == 'POST' and request.user.is_authenticated:
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            ProjectComment.objects.create(
                project=project,
                author=request.user,
                comment=comment_text
            )
            messages.success(request, "Fikringiz muvaffaqiyatli qo‘shildi!")
            return redirect('projects:project_detail', project_id=project.id)

    comments = project.comments.select_related('author').all()

    # Holatni o'zgartirish huquqi (mentor yoki admin)
    can_moderate = False
    if request.user.is_authenticated:
        if request.user.is_admin_user:
            can_moderate = True
        elif project.mentor and hasattr(request.user, 'teacher_profile') and request.user.teacher_profile == project.mentor:
            can_moderate = True

    context = {
        'project': project,
        'comments': comments,
        'can_moderate': can_moderate,
        'statuses': Project.Status.choices,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def project_status_update_view(request, project_id):
    """Loyiha holatini o'zgartirish (Ma'qullash, rad etish, yakunlash)"""
    project = get_object_or_404(Project, id=project_id)

    can_moderate = request.user.is_admin_user or (
        project.mentor and hasattr(request.user, 'teacher_profile') and request.user.teacher_profile == project.mentor
    )

    if not can_moderate:
        raise PermissionDenied("Sizda ushbu loyiha holatini o‘zgartirish huquqi yo‘q!")

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Project.Status.choices):
            project.status = new_status
            project.save()
            messages.success(request, f"Loyiha holati '{project.get_status_display()}'ga o‘zgartirildi.")

    return redirect('projects:project_detail', project_id=project.id)
