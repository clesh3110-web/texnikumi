from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.audit.models import AuditLog, log_audit

User = get_user_model()

class AuditTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="audit_admin",
            password="password123",
            role=User.Role.SUPERADMIN,
            first_name="Audit",
            last_name="Supervizor"
        )
        self.student = User.objects.create_user(
            username="audit_student",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Oddiy",
            last_name="Talaba"
        )
        self.log_entry = log_audit(
            user=self.admin,
            action=AuditLog.Action.LOGIN,
            details="Admin tizimga muvaffaqiyatli kirdi.",
            ip_address="127.0.0.1"
        )

    def test_log_audit_helper(self):
        self.assertEqual(AuditLog.objects.count(), 1)
        self.assertEqual(self.log_entry.action, AuditLog.Action.LOGIN)

    def test_student_cannot_access_audit_log(self):
        self.client.login(username="audit_student", password="password123")
        response = self.client.get(reverse('audit:audit_log'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_audit_log(self):
        self.client.login(username="audit_admin", password="password123")
        response = self.client.get(reverse('audit:audit_log'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin tizimga muvaffaqiyatli kirdi.")

    def test_audit_log_filtering(self):
        self.client.login(username="audit_admin", password="password123")
        response = self.client.get(reverse('audit:audit_log') + '?action=LOGIN')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin tizimga muvaffaqiyatli kirdi.")

        response_empty = self.client.get(reverse('audit:audit_log') + '?action=LOGOUT')
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, "Admin tizimga muvaffaqiyatli kirdi.")
