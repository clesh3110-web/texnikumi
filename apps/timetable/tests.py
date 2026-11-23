from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from apps.subjects.models import Subject, TeacherSubjectGroup
from apps.groups.models import Group
from apps.teachers.models import TeacherProfile
from apps.students.models import StudentProfile
from apps.library.models import Book, BookRequest
from apps.timetable.models import TimetableItem

User = get_user_model()

class TimetableTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.group = Group.objects.create(name="DI-21", course=1)

        # Subjects
        self.math_subj = Subject.objects.create(name="Oliy Matematika", code="MATH-101")
        self.eng_subj = Subject.objects.create(name="Ingliz tili", code="ENG-101")

        # Teacher
        self.teacher_user = User.objects.create_user(
            username="ustoz_time",
            password="password123",
            role=User.Role.TEACHER,
            first_name="Zarif",
            last_name="Rasulov"
        )
        self.teacher_profile = self.teacher_user.teacher_profile

        # Teaching assignment
        self.tsg_math = TeacherSubjectGroup.objects.create(
            teacher=self.teacher_profile,
            group=self.group,
            subject=self.math_subj
        )
        self.tsg_eng = TeacherSubjectGroup.objects.create(
            teacher=self.teacher_profile,
            group=self.group,
            subject=self.eng_subj
        )

        # Student
        self.student_user = User.objects.create_user(
            username="talaba_time",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Madina",
            last_name="Qosimova"
        )
        self.student_profile = self.student_user.student_profile
        self.student_profile.group = self.group
        self.student_profile.save()

        # Timetable Items
        self.item_math = TimetableItem.objects.create(
            group=self.group,
            weekday=1,
            lesson_pair=1,
            assignment=self.tsg_math,
            room="204-xona"
        )
        self.item_eng = TimetableItem.objects.create(
            group=self.group,
            weekday=1,
            lesson_pair=2,
            assignment=self.tsg_eng,
            room="110-xona"
        )

        # Book for Math only
        dummy_pdf = SimpleUploadedFile("math.pdf", b"%PDF-1.4 dummy", content_type="application/pdf")
        self.book_math = Book.objects.create(
            title="Matematika Darsligi",
            author="Zarif Rasulov",
            subject=self.math_subj,
            pdf_file=dummy_pdf,
            is_public=True
        )

    def test_timetable_view_requires_login(self):
        response = self.client.get(reverse('timetable:timetable_view'))
        self.assertEqual(response.status_code, 302)

    def test_student_timetable_view(self):
        self.client.login(username="talaba_time", password="password123")
        response = self.client.get(reverse('timetable:timetable_view'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oliy Matematika")
        self.assertContains(response, "Ingliz tili")
        self.assertContains(response, "204-xona")

    def test_timetable_item_with_book_redirects_to_library(self):
        self.client.login(username="talaba_time", password="password123")
        response = self.client.get(reverse('timetable:timetable_book_action', kwargs={'item_id': self.item_math.id}))
        self.assertRedirects(response, reverse('library:book_detail', kwargs={'book_id': self.book_math.id}))

    def test_timetable_item_without_book_prompts_request(self):
        self.client.login(username="talaba_time", password="password123")
        response = self.client.get(reverse('timetable:timetable_book_action', kwargs={'item_id': self.item_eng.id}))
        # Redirects with warning back to timetable with query param
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"missing_book_subject={self.eng_subj.id}", response.url)
