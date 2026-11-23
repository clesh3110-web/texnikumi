from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.groups.models import Group
from apps.projects.models import Project, ProjectComment

User = get_user_model()

class ProjectsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username="startup_student",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Bekzod",
            last_name="Rustamov"
        )
        self.admin = User.objects.create_user(
            username="admin_user",
            password="password123",
            role=User.Role.SUPERADMIN,
            first_name="Admin",
            last_name="Boshliq"
        )
        self.group = Group.objects.create(name="AT-21", course=1)

        self.project = Project.objects.create(
            title="Online Navbat Tizimi",
            creator=self.student,
            group=self.group,
            category=Project.Category.IT,
            description="Elektron navbat tizimi dasturi",
            status=Project.Status.REVIEW
        )

    def test_projects_list_view(self):
        response = self.client.get(reverse('projects:projects_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Online Navbat Tizimi")

    def test_project_create_view(self):
        self.client.login(username="startup_student", password="password123")
        response = self.client.post(reverse('projects:project_create'), {
            'title': 'Aqlli Chiroqlar',
            'category': Project.Category.AUTOMATION,
            'description': 'IoT asosidagi chiroqlar'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(title='Aqlli Chiroqlar').exists())

    def test_project_comment_view(self):
        self.client.login(username="startup_student", password="password123")
        detail_url = reverse('projects:project_detail', kwargs={'project_id': self.project.id})
        response = self.client.post(detail_url, {
            'comment': 'Loyiha ustida ish davom etmoqda.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProjectComment.objects.filter(project=self.project, comment='Loyiha ustida ish davom etmoqda.').exists())

    def test_admin_can_update_status(self):
        self.client.login(username="admin_user", password="password123")
        status_url = reverse('projects:project_status_update', kwargs={'project_id': self.project.id})
        response = self.client.post(status_url, {
            'status': Project.Status.APPROVED
        })
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.APPROVED)
