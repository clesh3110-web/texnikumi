from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.messaging.models import Message

User = get_user_model()

class MessagingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = User.objects.create_user(
            username="sender_user",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Jasur",
            last_name="Bekov"
        )
        self.recipient = User.objects.create_user(
            username="recipient_user",
            password="password123",
            role=User.Role.TEACHER,
            first_name="Nodira",
            last_name="Aliyeva"
        )
        self.message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject="Dars haqida savol",
            body="Assalomu alaykum ustoz, ertaga dars bo‘ladimi?"
        )

    def test_inbox_requires_login(self):
        response = self.client.get(reverse('messaging:inbox'))
        self.assertEqual(response.status_code, 302)

    def test_inbox_view(self):
        self.client.login(username="recipient_user", password="password123")
        response = self.client.get(reverse('messaging:inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dars haqida savol")

    def test_sent_view(self):
        self.client.login(username="sender_user", password="password123")
        response = self.client.get(reverse('messaging:sent'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dars haqida savol")

    def test_message_detail_marks_read(self):
        self.client.login(username="recipient_user", password="password123")
        self.assertFalse(self.message.is_read)
        response = self.client.get(reverse('messaging:message_detail', kwargs={'message_id': self.message.id}))
        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)

    def test_delete_message(self):
        self.client.login(username="sender_user", password="password123")
        response = self.client.get(reverse('messaging:delete_message', kwargs={'message_id': self.message.id}))
        self.assertEqual(response.status_code, 302)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_deleted_by_sender)
