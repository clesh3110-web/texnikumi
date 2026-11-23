from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.students.models import StudentProfile
from apps.core.models import News, Announcement, Leadership, ContactMessage

class PublicWebAndAdminDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin user
        self.admin_user = User.objects.create_user(
            username='admin_tester',
            password='Password123!',
            role=User.Role.ADMIN
        )

        # Student user
        self.student_user = User.objects.create_user(
            username='student_tester',
            password='Password123!',
            role=User.Role.STUDENT
        )

        # Teacher & Group
        self.teacher_user = User.objects.create_user(
            username='teacher_tester',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Zohid',
            last_name='Nazarov'
        )
        self.teacher_profile = TeacherProfile.objects.get(user=self.teacher_user)
        self.group = Group.objects.create(
            name='DI-21',
            course=Group.Course.SECOND,
            direction='Dasturiy injiniring',
            curator=self.teacher_profile
        )

    def test_public_home_page(self):
        """Ommaviy bosh sahifa muvaffaqiyatli ochilishi (200)"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GULISTON 1-SON TEXNIKUM")

    def test_public_contact_form_submission(self):
        """Aloqa sahifasidan murojaat yuborishni tekshirish"""
        response = self.client.post(reverse('core:contact'), {
            'full_name': 'Alisher Valiyev',
            'phone': '+998901234567',
            'email': 'alisher@test.uz',
            'subject': 'Qabul masalasi',
            'message': 'Texnikumga qabul qoidalari haqida ma‘lumot bering.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.first().full_name, 'Alisher Valiyev')

    def test_admin_dashboard_security_unauthenticated(self):
        """Kirilmagan holda dashboardga kirish taqiqlanishi (login sahifasiga redirect)"""
        response = self.client.get(reverse('core:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_admin_dashboard_access_by_admin(self):
        """Administrator dashboardga kirishi va statistikalarni ko'rishi"""
        self.client.login(username='admin_tester', password='Password123!')
        response = self.client.get(reverse('core:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Boshqaruv Dashboardi va Monitoring")
        self.assertIn('groups_monitoring', response.context)
        self.assertIn('total_students', response.context)

    def test_admin_group_detail_page(self):
        """Guruh alohida sahifasini ko'rish"""
        self.client.login(username='admin_tester', password='Password123!')
        response = self.client.get(reverse('core:admin_group_detail', kwargs={'group_id': self.group.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DI-21")
        self.assertContains(response, "Dasturiy injiniring")
