from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.subjects.models import Subject, TeacherSubjectGroup
from apps.students.models import StudentProfile

class TeacherDashboardAndPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Teacher 1
        self.teacher1_user = User.objects.create_user(
            username='teacher1',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Dilorom',
            last_name='Karimova'
        )
        self.teacher1_profile = TeacherProfile.objects.get(user=self.teacher1_user)

        # Teacher 2 (Unassigned)
        self.teacher2_user = User.objects.create_user(
            username='teacher2',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Rustam',
            last_name='Yusupov'
        )
        self.teacher2_profile = TeacherProfile.objects.get(user=self.teacher2_user)

        # Group DI-21
        self.group = Group.objects.create(
            name='DI-21',
            course=Group.Course.SECOND,
            direction='Dasturiy injiniring',
            curator=self.teacher1_profile
        )

        # Subject & Assignment for Teacher 1
        self.subject = Subject.objects.create(
            name='Veb-dasturlash',
            code='WEB-201',
            total_hours=72
        )
        TeacherSubjectGroup.objects.create(
            teacher=self.teacher1_profile,
            subject=self.subject,
            group=self.group
        )

        # Student in DI-21
        self.student_user = User.objects.create_user(
            username='student1',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Javohir',
            last_name='Toshtemirov'
        )
        self.student_profile = StudentProfile.objects.get(user=self.student_user)
        self.student_profile.group = self.group
        self.student_profile.save()

    def test_teacher_dashboard_access(self):
        """O'qituvchi o'z paneliga kira olishi (200)"""
        self.client.login(username='teacher1', password='Password123!')
        response = self.client.get(reverse('teachers:teacher_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Karimova Dilorom")
        self.assertContains(response, "Mening Guruhlarim")

    def test_teacher_can_access_assigned_group(self):
        """O'qituvchi o'ziga biriktirilgan guruh sahifasiga kira olishi (200)"""
        self.client.login(username='teacher1', password='Password123!')
        response = self.client.get(reverse('teachers:teacher_group_detail', kwargs={'group_id': self.group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DI-21")

    def test_teacher_cannot_access_unassigned_group(self):
        """O'qituvchi biriktirilmagan begona guruhga kira olmasligi (403 PermissionDenied)"""
        self.client.login(username='teacher2', password='Password123!')
        response = self.client.get(reverse('teachers:teacher_group_detail', kwargs={'group_id': self.group.id}))
        self.assertEqual(response.status_code, 403)
