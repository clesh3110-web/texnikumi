import datetime
from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.subjects.models import Subject, TeacherSubjectGroup
from apps.students.models import StudentProfile
from apps.journal.models import Grade, GradeAuditLog

class JournalAndGradingTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Teacher
        self.teacher_user = User.objects.create_user(
            username='teacher_karimova',
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
            name='Veb-dasturlash',
            code='WEB-201',
            total_hours=72
        )
        self.assignment = TeacherSubjectGroup.objects.create(
            teacher=self.teacher_profile,
            subject=self.subject,
            group=self.group
        )

        # Student
        self.student_user = User.objects.create_user(
            username='student_toshtemirov',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Javohir',
            last_name='Toshtemirov'
        )
        self.student_profile = StudentProfile.objects.get(user=self.student_user)
        self.student_profile.group = self.group
        self.student_profile.save()

    def test_teacher_can_enter_grade(self):
        """O'qituvchi o'quvchiga 5 ballik baho qo'ya olishi"""
        self.client.login(username='teacher_karimova', password='Password123!')
        response = self.client.post(
            f"{reverse('journal:journal_view')}?assignment={self.assignment.id}",
            {
                'student_id': self.student_profile.id,
                'lesson_date': '2026-11-08',
                'score': '5',
                'grade_type': Grade.GradeType.CURRENT,
                'comment': 'A‘lo javob berdi',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Grade.objects.count(), 1)
        grade = Grade.objects.first()
        self.assertEqual(grade.score, 5)
        self.assertEqual(grade.student, self.student_profile)

    def test_grade_edit_creates_audit_log(self):
        """Baho o'zgartirilganda Audit tarixida yozuv qolishi (Section 8 & 24)"""
        grade = Grade.objects.create(
            student=self.student_profile,
            assignment=self.assignment,
            lesson_date=datetime.date(2026, 11, 8),
            score=4,
            grade_type=Grade.GradeType.CURRENT,
            created_by=self.teacher_user
        )

        self.client.login(username='teacher_karimova', password='Password123!')
        # Bahoni 4 dan 5 ga o'zgartirish
        response = self.client.post(
            f"{reverse('journal:journal_view')}?assignment={self.assignment.id}",
            {
                'student_id': self.student_profile.id,
                'lesson_date': '2026-11-08',
                'score': '5',
                'grade_type': Grade.GradeType.CURRENT,
                'audit_reason': 'Qayta topshirib a‘lo baho oldi',
            }
        )
        self.assertEqual(response.status_code, 302)
        grade.refresh_from_db()
        self.assertEqual(grade.score, 5)

        # Audit yozuvini tekshirish
        self.assertEqual(GradeAuditLog.objects.count(), 1)
        log = GradeAuditLog.objects.first()
        self.assertEqual(log.old_score, 4)
        self.assertEqual(log.new_score, 5)
        self.assertEqual(log.changed_by, self.teacher_user)
