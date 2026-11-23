import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User
from apps.teachers.models import TeacherProfile
from apps.groups.models import Group
from apps.students.models import StudentProfile
from apps.documents.models import AttendanceDocument

class DocumentsAndMedicalPrivacyTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin
        self.admin_user = User.objects.create_user(
            username='admin_doc',
            password='Password123!',
            role=User.Role.ADMIN
        )

        # Curator Teacher
        self.curator_user = User.objects.create_user(
            username='curator_doc',
            password='Password123!',
            role=User.Role.TEACHER,
            first_name='Dilorom',
            last_name='Karimova'
        )
        self.curator = TeacherProfile.objects.get(user=self.curator_user)

        # Unrelated Teacher
        self.other_teacher_user = User.objects.create_user(
            username='other_teacher',
            password='Password123!',
            role=User.Role.TEACHER
        )

        # Group
        self.group = Group.objects.create(name='DI-21', curator=self.curator)

        # Student 1 (Document owner)
        self.student1_user = User.objects.create_user(
            username='student_owner',
            password='Password123!',
            role=User.Role.STUDENT,
            first_name='Javohir',
            last_name='Toshtemirov'
        )
        self.student1 = StudentProfile.objects.get(user=self.student1_user)
        self.student1.group = self.group
        self.student1.save()

        # Student 2 (Other student)
        self.student2_user = User.objects.create_user(
            username='other_student',
            password='Password123!',
            role=User.Role.STUDENT
        )

        # Dummy file
        dummy_pdf = SimpleUploadedFile("spravka.pdf", b"%PDF-1.4 test document content", content_type="application/pdf")

        # Document
        self.document = AttendanceDocument.objects.create(
            student=self.student1,
            group=self.group,
            doc_type=AttendanceDocument.DocType.SPRAVKA,
            start_date=datetime.date(2026, 11, 1),
            end_date=datetime.date(2026, 11, 4),
            reason='Tana harorati 38C, shamollash',
            file=dummy_pdf,
            status=AttendanceDocument.Status.NEW
        )

    def test_owner_student_can_view_own_document(self):
        """O'quvchi o'z spravkasini ko'ra olishi (200)"""
        self.client.login(username='student_owner', password='Password123!')
        response = self.client.get(reverse('documents:document_detail', kwargs={'doc_id': self.document.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "shamollash")

    def test_other_student_cannot_view_medical_document(self):
        """XAVFSIZLIK: Boshqa o'quvchi birovning tibbiy spravkasini KO'RA OLMAYDI (403)"""
        self.client.login(username='other_student', password='Password123!')
        response = self.client.get(reverse('documents:document_detail', kwargs={'doc_id': self.document.id}))
        self.assertEqual(response.status_code, 403)

    def test_curator_can_view_student_document(self):
        """Guruh rahbari (kurator) o'z o'quvchisining spravkasini ko'ra olishi (200)"""
        self.client.login(username='curator_doc', password='Password123!')
        response = self.client.get(reverse('documents:document_detail', kwargs={'doc_id': self.document.id}))
        self.assertEqual(response.status_code, 200)

    def test_unrelated_teacher_cannot_view_medical_document(self):
        """XAVFSIZLIK: Aloqasi bo'lmagan begona o'qituvchi boshqa guruh spravkasini KO'RA OLMAYDI (403)"""
        self.client.login(username='other_teacher', password='Password123!')
        response = self.client.get(reverse('documents:document_detail', kwargs={'doc_id': self.document.id}))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_approve_document(self):
        """Administrator hujjatni tasdiqlashi (APPROVED)"""
        self.client.login(username='admin_doc', password='Password123!')
        response = self.client.post(reverse('documents:documents_list'), {
            'doc_id': self.document.id,
            'status': AttendanceDocument.Status.APPROVED,
            'review_comment': 'Poliklinika muhriga ega, tasdiqlandi',
        })
        self.assertEqual(response.status_code, 302)
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, AttendanceDocument.Status.APPROVED)
        self.assertEqual(self.document.reviewed_by, self.admin_user)
