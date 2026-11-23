from django.test import TestCase
from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.students.models import StudentProfile

class GroupAndAcademicTests(TestCase):
    def setUp(self):
        # Teacher
        self.teacher_user = User.objects.create_user(
            username='prof_karimova',
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

        # Student
        self.student_user = User.objects.create_user(
            username='stud_toshtemirov',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Javohir',
            last_name='Toshtemirov'
        )
        self.student_profile = StudentProfile.objects.get(user=self.student_user)
        self.student_profile.group = self.group
        self.student_profile.save()

    def test_group_creation_and_curator(self):
        self.assertEqual(self.group.name, 'DI-21')
        self.assertEqual(self.group.curator, self.teacher_profile)
        self.assertEqual(self.group.total_students_count, 1)

    def test_student_belongs_to_group(self):
        self.assertEqual(self.student_profile.group, self.group)
        self.assertIn(self.student_profile, self.group.students.all())
