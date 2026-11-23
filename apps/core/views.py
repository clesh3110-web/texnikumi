import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from apps.attendance.models import Attendance
from apps.accounts.permissions import admin_required
from apps.students.models import StudentProfile
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.subjects.models import Subject, TeacherSubjectGroup
from .models import News, Announcement, Leadership, ContactMessage

# ==========================================================
# 1. OMMAVIY SAHIFALAR (PUBLIC PAGES)
# ==========================================================

def home_view(request):
    """Texnikumning rasmiy bosh sahifasi"""
    context = {
        'total_students': StudentProfile.objects.count(),
        'total_teachers': TeacherProfile.objects.count(),
        'total_groups': Group.objects.count(),
        'total_subjects': Subject.objects.count(),
        'latest_news': News.objects.filter(is_published=True)[:3],
        'announcements': Announcement.objects.filter(is_active=True)[:4],
        'leaders': Leadership.objects.all()[:4],
        'groups': Group.objects.all()[:6],
    }
    return render(request, 'public/home.html', context)


def about_view(request):
    """Biz haqimizda sahifasi"""
    leaders = Leadership.objects.all()
    return render(request, 'public/about.html', {'leaders': leaders})


def leadership_view(request):
    """Texnikum rahbariyati sahifasi"""
    leaders = Leadership.objects.all()
    return render(request, 'public/leadership.html', {'leaders': leaders})


def departments_view(request):
    """Ta'lim yo'nalishlari sahifasi"""
    directions = [
        {
            'name': 'Dasturiy injiniring (Software Engineering)',
            'code': '5.06120101',
            'duration': '2 yil',
            'description': 'Zamonaviy dasturlash tillari (Python, JavaScript, Django), ma‘lumotlar bazasi va dasturiy ta‘minot arxitekturasi.',
            'icon': 'bi-laptop'
        },
        {
            'name': 'Axborot texnologiyalari (IT)',
            'code': '5.06110101',
            'duration': '2 yil',
            'description': 'Kompyuter tarmoqlari, tizimli ma‘murlash, kiberxavfsizlik asoslari va texnik xizmat ko‘rsatish.',
            'icon': 'bi-hdd-network'
        },
        {
            'name': 'Buxgalteriya hisobi va audit',
            'code': '5.04110101',
            'duration': '2 yil',
            'description': 'Moliyaviy hisobotlar, 1C Buxgalteriya, soliqqa tortish va avtomatlashtirilgan hisob-kitoblar.',
            'icon': 'bi-calculator'
        },
    ]
    return render(request, 'public/departments.html', {'directions': directions})


def news_list_view(request):
    """Yangiliklar ro'yxati"""
    news_list = News.objects.filter(is_published=True)
    paginator = Paginator(news_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'public/news_list.html', {'page_obj': page_obj})


def news_detail_view(request, pk):
    """Yangilik batafsil sahifasi"""
    news_item = get_object_or_404(News, pk=pk, is_published=True)
    news_item.views_count += 1
    news_item.save(update_fields=['views_count'])
    recent_news = News.objects.filter(is_published=True).exclude(pk=pk)[:4]
    return render(request, 'public/news_detail.html', {'news': news_item, 'recent_news': recent_news})


def contact_view(request):
    """Bog'lanish sahifasi va murojaat qabul qilish"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if full_name and phone and message:
            ContactMessage.objects.create(
                full_name=full_name,
                phone=phone,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, "Murojaatingiz qabul qilindi. Tez orada siz bilan bog‘lanamiz!")
            return redirect('core:contact')
        else:
            messages.error(request, "Iltimos, barcha majburiy maydonlarni to‘ldiring.")

    return render(request, 'public/contact.html')


# ==========================================================
# 2. ADMINISTRATOR BOSHQARUV PANELI (ADMIN DASHBOARD)
# ==========================================================

@admin_required
def admin_dashboard_view(request):
    """
    Administrator boshqaruv dashboardi va Guruhlar monitoringi.
    8 ta asosiy statistik ko'rsatkich va guruhlar bo'yicha Chart.js diagrammalari.
    """
    total_students = StudentProfile.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_groups = Group.objects.count()
    today_events_count = Announcement.objects.filter(is_active=True).count()

    # Davomat faqat bazadagi bugungi yozuvlardan hisoblanadi.
    groups = Group.objects.all().select_related('curator__user')
    groups_monitoring = []
    today = timezone.localdate()
    agg_present = agg_late = agg_sick = agg_absent = 0

    for g in groups:
        records = Attendance.objects.filter(group=g, date=today)
        present = records.filter(status=Attendance.Status.PRESENT).count()
        late = records.filter(status=Attendance.Status.LATE).count()
        sick = records.filter(status=Attendance.Status.SICK).count()
        absent = records.filter(status=Attendance.Status.ABSENT).count()
        marked_total = present + late + sick + absent
        attendance_percent = round((present + late) / marked_total * 100, 1) if marked_total else 0

        agg_present += present
        agg_late += late
        agg_sick += sick
        agg_absent += absent
        groups_monitoring.append({
            'group': g,
            'total': g.total_students_count,
            'present': present,
            'late': late,
            'sick': sick,
            'absent': absent,
            'attendance_percent': attendance_percent,
            'chart_data_json': json.dumps([present, late, sick, absent]),
        })

    grand_total = agg_present + agg_late + agg_sick + agg_absent
    overall_attendance_percent = round((agg_present + agg_late) / grand_total * 100, 1) if grand_total else 0

    context = {
        # 8 ta statistik karta ko'rsatkichlari:
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_groups': total_groups,
        'today_events': today_events_count,
        'today_attendance_percent': overall_attendance_percent,
        'today_absent': agg_absent,
        'today_sick': agg_sick,
        'today_late': agg_late,

        # Guruhlar monitoringi
        'groups_monitoring': groups_monitoring,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def admin_group_detail_view(request, group_id):
    """Guruh kartasini bosganda ochiladigan alohida batafsil sahifa"""
    group = get_object_or_404(Group.objects.select_related('curator__user'), id=group_id)
    students = group.students.select_related('user').all()
    assignments = group.teaching_assignments.select_related('teacher__user', 'subject').all()

    # Guruh davomati bugungi real yozuvlardan hisoblanadi.
    today = timezone.localdate()
    records = Attendance.objects.filter(group=group, date=today)
    present = records.filter(status=Attendance.Status.PRESENT).count()
    late = records.filter(status=Attendance.Status.LATE).count()
    sick = records.filter(status=Attendance.Status.SICK).count()
    absent = records.filter(status=Attendance.Status.ABSENT).count()
    marked_total = present + late + sick + absent
    attendance_percent = round((present + late) / marked_total * 100, 1) if marked_total else 0

    context = {
        'group': group,
        'students': students,
        'assignments': assignments,
        'total_students': total,
        'present': present,
        'late': late,
        'sick': sick,
        'absent': absent,
        'attendance_percent': attendance_percent,
        'chart_data_json': json.dumps([present, late, sick, absent]),
    }
    return render(request, 'admin_panel/group_detail.html', context)


@admin_required
def admin_students_list_view(request):
    """Barcha o'quvchilar ro'yxati va monitoring jadvali"""
    query = request.GET.get('q', '').strip()
    group_filter = request.GET.get('group', '').strip()
    status_filter = request.GET.get('status', '').strip()

    students = StudentProfile.objects.select_related('user', 'group').all()

    if query:
        students = students.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__phone__icontains=query) |
            Q(student_id_number__icontains=query)
        )
    if group_filter:
        students = students.filter(group__name=group_filter)
    if status_filter:
        students = students.filter(status=status_filter)

    paginator = Paginator(students, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'groups': Group.objects.all(),
        'query': query,
        'group_filter': group_filter,
        'status_filter': status_filter,
        'total_count': students.count(),
    }
    return render(request, 'admin_panel/students_list.html', context)


@admin_required
def admin_teachers_list_view(request):
    """Barcha o'qituvchilar ro'yxati"""
    query = request.GET.get('q', '').strip()
    teachers = TeacherProfile.objects.select_related('user').prefetch_related('teaching_assignments__subject').all()

    if query:
        teachers = teachers.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__phone__icontains=query) |
            Q(department__icontains=query) |
            Q(specialization__icontains=query)
        )

    context = {
        'teachers': teachers,
        'query': query,
        'total_count': teachers.count(),
    }
    return render(request, 'admin_panel/teachers_list.html', context)
