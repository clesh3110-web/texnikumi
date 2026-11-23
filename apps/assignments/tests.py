import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.subjects.models import Subject, TeacherSubjectGroup
from apps.groups.models import Group
from apps.teachers.models import TeacherProfile
from apps.students.models import StudentProfile
from apps.assignments.models import Assignment, AssignmentSubmission

User = get_user_model()

class AssignmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = Group.objects.create(name="DI-21", course=1)
        self.subject = Subject.objects.create(name="Veb Dasturlash", code="WEB-101")

        # Teacher
        self.teacher_user = User.objects.create_user(
            username="ustoz_assign",
            password="password123",
            role=User.Role.TEACHER,
            first_name="Dilshod",
            last_name="Bekov"
        )
        self.teacher_profile = self.teacher_user.teacher_profile

        self.tsg = TeacherSubjectGroup.objects.create(
            teacher=self.teacher_profile,
            group=self.group,
            subject=self.subject
        )

        # Student
        self.student_user = User.objects.create_user(
            username="talaba_assign",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Anvar",
            last_name="Saidov"
        )
        self.student_profile = self.student_user.student_profile
        self.student_profile.group = self.group
        self.student_profile.save()

        # Assignment
        self.assignment = Assignment.objects.create(
            assignment=self.tsg,
            title="HTML va CSS asoslari",
            topic="Frontend",
            description="Shaxsiy veb-sahifa tayyorlang",
            due_date=timezone.now() + datetime.timedelta(days=7),
            created_by=self.teacher_user
        )

    def test_assignment_list_requires_login(self):
        response = self.client.get(reverse('assignments:assignment_list'))
        self.assertEqual(response.status_code, 302)

    def test_student_can_see_assignments(self):
        self.client.login(username="talaba_assign", password="password123")
        response = self.client.get(reverse('assignments:assignment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HTML va CSS asoslari")

    def test_student_submission_flow(self):
        self.client.login(username="talaba_assign", password="password123")
        detail_url = reverse('assignments:assignment_detail', kwargs={'task_id': self.assignment.id})
        
        # View detail
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)

        # Submit solution
        response_post = self.client.post(detail_url, {
            'submit_solution': '1',
            'submission_text': 'Mening yechimim: index.html va style.css fayllari tayyorlandi.'
        })
        self.assertEqual(response_post.status_code, 302)

        submission = AssignmentSubmission.objects.get(assignment=self.assignment, student=self.student_profile)
        self.assertEqual(submission.status, AssignmentSubmission.Status.SUBMITTED)
        self.assertEqual(submission.submission_text, 'Mening yechimim: index.html va style.css fayllari tayyorlandi.')

    def test_teacher_grading_flow(self):
        # Create submission
        submission = AssignmentSubmission.objects.create(
            assignment=self.assignment,
            student=self.student_profile,
            submission_text="Yechim tayyor",
            status=AssignmentSubmission.Status.SUBMITTED,
            submitted_at=timezone.now()
        )

        # Teacher grades it
        self.client.login(username="ustoz_assign", password="password123")
        detail_url = reverse('assignments:assignment_detail', kwargs={'task_id': self.assignment.id})

        grade_post = self.client.post(detail_url, {
            'grade_submission': '1',
            'submission_id': submission.id,
            'score': 5,
            'teacher_feedback': 'Juda yaxshi bajarilgan!',
            'action_type': 'GRADED'
        })
        self.assertEqual(grade_post.status_code, 302)

        submission.refresh_from_db()
        self.assertEqual(submission.status, AssignmentSubmission.Status.GRADED)
        self.assertEqual(submission.score, 5)
        self.assertEqual(submission.teacher_feedback, 'Juda yaxshi bajarilgan!')

    def test_student_cannot_create_assignment(self):
        self.client.login(username="talaba_assign", password="password123")
        response = self.client.get(reverse('assignments:assignment_create'))
        self.assertEqual(response.status_code, 403)
