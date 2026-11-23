from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from apps.subjects.models import Subject
from apps.groups.models import Group
from apps.students.models import StudentProfile
from apps.library.models import Book, BookRequest

User = get_user_model()

class LibraryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.subject = Subject.objects.create(name="Matematika", code="MATH-101")
        self.group = Group.objects.create(name="DI-21", course=1)

        self.student_user = User.objects.create_user(
            username="talaba_lib",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Alisher",
            last_name="Navoiy"
        )
        self.student_profile = self.student_user.student_profile
        self.student_profile.group = self.group
        self.student_profile.save()

        dummy_pdf = SimpleUploadedFile("math_book.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        self.book = Book.objects.create(
            title="Oliy Matematika",
            author="Toshmatov",
            subject=self.subject,
            isbn="978-1234567890",
            pdf_file=dummy_pdf,
            is_public=True
        )

    def test_book_str(self):
        self.assertEqual(str(self.book), "Oliy Matematika — Toshmatov")

    def test_catalog_view(self):
        response = self.client.get(reverse('library:catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oliy Matematika")
        self.assertContains(response, "Toshmatov")

    def test_catalog_search(self):
        response = self.client.get(reverse('library:catalog') + '?q=Matematika')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oliy Matematika")

        response_empty = self.client.get(reverse('library:catalog') + '?q=Biologiya')
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, "Oliy Matematika")

    def test_book_detail_and_views_count(self):
        initial_views = self.book.views_count
        response = self.client.get(reverse('library:book_detail', kwargs={'book_id': self.book.id}))
        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.views_count, initial_views + 1)

    def test_book_download_redirect_and_counter(self):
        initial_downloads = self.book.downloads_count
        response = self.client.get(reverse('library:book_detail', kwargs={'book_id': self.book.id}) + '?download=1')
        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.downloads_count, initial_downloads + 1)

    def test_book_request_creation(self):
        self.client.login(username="talaba_lib", password="password123")
        response = self.client.get(reverse('timetable:request_book', kwargs={'subject_id': self.subject.id}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BookRequest.objects.filter(student=self.student_profile, subject=self.subject).exists())
