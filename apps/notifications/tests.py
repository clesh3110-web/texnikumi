from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification
from apps.notifications.utils import send_notification

User = get_user_model()

class NotificationsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="notif_user",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Lobar",
            last_name="Saidova"
        )
        self.notif = send_notification(
            recipient=self.user,
            title="Dars vaqti o‘zgardi",
            message="Ertangi dars soat 09:00 ga ko‘chirildi.",
            link_url="/timetable/",
            notification_type=Notification.Type.INFO
        )

    def test_notifications_list_view(self):
        self.client.login(username="notif_user", password="password123")
        response = self.client.get(reverse('notifications:notifications_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dars vaqti o‘zgardi")

    def test_mark_as_read_redirects(self):
        self.client.login(username="notif_user", password="password123")
        self.assertFalse(self.notif.is_read)
        response = self.client.get(reverse('notifications:mark_read', kwargs={'notif_id': self.notif.id}))
        self.assertRedirects(response, "/timetable/")
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)

    def test_unread_count_api(self):
        self.client.login(username="notif_user", password="password123")
        response = self.client.get(reverse('notifications:unread_count_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['unread_count'], 1)
