from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.groups.models import Group
from apps.students.models import StudentProfile

User = get_user_model()

class ReportsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="reports_admin",
            password="password123",
            role=User.Role.ADMIN,
            first_name="Hisobchi",
            last_name="Nazoratchi"
        )
        self.group = Group.objects.create(name="DI-21", course=1)

        self.student_user = User.objects.create_user(
            username="reports_student",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Temur",
            last_name="Bek"
        )
        self.student_profile = self.student_user.student_profile
        self.student_profile.group = self.group
        self.student_profile.save()

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_admin_can_access_dashboard(self):
        self.client.login(username="reports_admin", password="password123")
        response = self.client.get(reverse('reports:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hisobotlar, Vedomostlar va Eksport")

    def test_export_attendance_excel(self):
        self.client.login(username="reports_admin", password="password123")
        response = self.client.get(reverse('reports:export_attendance_excel') + f"?group_id={self.group.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_export_grades_excel(self):
        self.client.login(username="reports_admin", password="password123")
        response = self.client.get(reverse('reports:export_grades_excel') + f"?group_id={self.group.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_export_transcript_pdf(self):
        self.client.login(username="reports_admin", password="password123")
        url = reverse('reports:export_student_transcript_pdf', kwargs={'student_id': self.student_profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
