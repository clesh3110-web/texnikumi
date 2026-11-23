from django.test import TestCase
from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.subjects.models import Subject, TeacherSubjectGroup

class SubjectAndAssignmentTests(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(
            username='prof_python',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Ali',
            last_name='Valiyev'
        )
        self.teacher_profile = TeacherProfile.objects.get(user=self.teacher_user)

        self.group = Group.objects.create(
            name='AT-21',
            course=Group.Course.FIRST,
            direction='Axborot texnologiyalari'
        )

        self.subject = Subject.objects.create(
            name='Python dasturlash',
            code='CS-101',
            total_hours=90
        )

        self.assignment = TeacherSubjectGroup.objects.create(
            teacher=self.teacher_profile,
            subject=self.subject,
            group=self.group,
            academic_year='2024-2025',
            semester=1
        )

    def test_teaching_assignment_relation(self):
        self.assertEqual(self.assignment.teacher, self.teacher_profile)
        self.assertEqual(self.assignment.subject, self.subject)
        self.assertEqual(self.assignment.group, self.group)
        self.assertEqual(self.teacher_profile.teaching_assignments.count(), 1)
        self.assertEqual(self.group.teaching_assignments.count(), 1)
