import datetime
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.students.models import StudentProfile
from apps.attendance.models import Attendance

class AttendanceTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin
        self.admin_user = User.objects.create_user(
            username='admin_attend',
            password='Password123!',
            role=User.Role.ADMIN
        )

        # Group & Student
        self.group = Group.objects.create(name='DI-21', course=Group.Course.SECOND)
        self.student_user = User.objects.create_user(
            username='stud_attend',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Jasur',
            last_name='Xoliqov'
        )
        self.student = StudentProfile.objects.get(user=self.student_user)
        self.student.group = self.group
        self.student.save()

    def test_record_attendance(self):
        """Davomat yozuvi yaratish (Darsda, Kechikdi, Kasallik, Boshqa sabab)"""
        att = Attendance.objects.create(
            student=self.student,
            group=self.group,
            date=datetime.date(2026, 11, 8),
            lesson_pair=1,
            status=Attendance.Status.PRESENT,
            marked_by=self.admin_user
        )
        self.assertEqual(Attendance.objects.count(), 1)
        self.assertEqual(att.status, Attendance.Status.PRESENT)

    def test_bulk_attendance_post(self):
        """Web forma orqali davomatni saqlash"""
        self.client.login(username='admin_attend', password='Password123!')
        response = self.client.post(
            f"{reverse('attendance:attendance_view')}?group={self.group.id}&date=2026-11-08&pair=1",
            {
                f'status_{self.student.id}': Attendance.Status.LATE,
                f'comment_{self.student.id}': '10 daqiqa kechikdi',
            }
        )
        self.assertEqual(response.status_code, 302)
        att = Attendance.objects.get(student=self.student, date=datetime.date(2026, 11, 8), lesson_pair=1)
        self.assertEqual(att.status, Attendance.Status.LATE)
        self.assertEqual(att.comment, '10 daqiqa kechikdi')
