from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.subjects.models import Subject, TeacherSubjectGroup
from apps.students.models import StudentProfile

class StudentDashboardAndPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Teacher
        self.teacher_user = User.objects.create_user(
            username='teacher_dilorom',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Dilorom',
            last_name='Karimova'
        )
        self.teacher_profile = TeacherProfile.objects.get(user=self.teacher_user)

        # Group
        self.group = Group.objects.create(
            name='DI-21',
            course=Group.Course.SECOND,
            direction='Dasturiy injiniring',
            curator=self.teacher_profile
        )

        # Subject & Assignment
        self.subject = Subject.objects.create(
            name='Python dasturlash',
            code='CS-101',
            total_hours=90
        )
        TeacherSubjectGroup.objects.create(
            teacher=self.teacher_profile,
            subject=self.subject,
            group=self.group
        )

        # Student
        self.student_user = User.objects.create_user(
            username='student_javohir',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Javohir',
            last_name='Toshtemirov'
        )
        self.student_profile = StudentProfile.objects.get(user=self.student_user)
        self.student_profile.group = self.group
        self.student_profile.student_id_number = 'GT-2024-0001'
        self.student_profile.save()

    def test_student_dashboard_access(self):
        """O'quvchi o'z paneliga kira olishi (200)"""
        self.client.login(username='student_javohir', password='Password123!')
        response = self.client.get(reverse('students:student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toshtemirov Javohir")
        self.assertContains(response, "DI-21 guruhi")

    def test_student_my_teachers_page(self):
        """O'quvchi o'z ustozlarini ko'ra olishi (200)"""
        self.client.login(username='student_javohir', password='Password123!')
        response = self.client.get(reverse('students:student_teachers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Karimova Dilorom")
        self.assertContains(response, "Python dasturlash")

    def test_student_cannot_access_admin_dashboard(self):
        """O'quvchi admin dashboardga kira olmasligi (403 PermissionDenied)"""
        self.client.login(username='student_javohir', password='Password123!')
        response = self.client.get(reverse('core:admin_dashboard'))
        self.assertEqual(response.status_code, 403)
