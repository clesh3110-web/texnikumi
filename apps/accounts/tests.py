from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User

class AccountsModelAndAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Superadmin
        self.superadmin = User.objects.create_user(
            username='test_superadmin',
            email='super@test.uz',
            phone='+998901111111',
            password='Password123!',
            role=User.Role.SUPERADMIN
        )
        # O'qituvchi
        self.teacher = User.objects.create_user(
            username='test_teacher',
            email='teacher@test.uz',
            phone='+998902222222',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Anvar',
            last_name='Nazarov'
        )
        # O'quvchi
        self.student = User.objects.create_user(
            username='test_student',
            email='student@test.uz',
            phone='+998903333333',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Dilshod',
            last_name='Karimov'
        )

    def test_custom_user_roles_and_properties(self):
        """Rollar va xususiyatlar to'g'ri ishlashini tekshirish"""
        self.assertTrue(self.superadmin.is_superadmin)
        self.assertTrue(self.superadmin.is_staff)
        self.assertTrue(self.superadmin.is_superuser)

        self.assertTrue(self.teacher.is_teacher)
        self.assertFalse(self.teacher.is_student)
        self.assertEqual(self.teacher.get_full_name_uz, "Nazarov Anvar")

        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_teacher)

    def test_login_with_username(self):
        """Username orqali tizimga kirishni tekshirish"""
        response = self.client.post(reverse('accounts:login'), {
            'login_field': 'test_teacher',
            'password': 'Password123!',
        })
        # Muvaffaqiyatli login redirekt qiladi (302)
        self.assertEqual(response.status_code, 302)

    def test_login_with_phone(self):
        """Telefon raqami orqali tizimga kirishni tekshirish"""
        response = self.client.post(reverse('accounts:login'), {
            'login_field': '+998903333333',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_password(self):
        """Noto'g'ri parol kiritilganda xatolik berishini tekshirish"""
        response = self.client.post(reverse('accounts:login'), {
            'login_field': 'test_student',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Kiritilgan login yoki parol noto‘g‘ri. Iltimos, qaytadan tekshirib ko‘ring.",
            form.non_field_errors()
        )

    def test_logout(self):
        """Chiqish (Logout) to'g'ri ishlashini tekshirish"""
        self.client.login(username='test_student', password='Password123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))
