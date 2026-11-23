import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.events.models import Event, EventParticipant

User = get_user_model()

class EventsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="event_student",
            password="password123",
            role=User.Role.STUDENT,
            first_name="Sanjar",
            last_name="Valiyev"
        )
        self.event = Event.objects.create(
            title="Texnikum bayrami",
            description="Katta bayram tadbiri",
            event_date=timezone.now() + datetime.timedelta(days=3),
            location="Faollar zali",
            organizer="Kafedra",
            max_participants=50
        )

    def test_events_list_view(self):
        response = self.client.get(reverse('events:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Texnikum bayrami")

    def test_event_detail_view(self):
        response = self.client.get(reverse('events:event_detail', kwargs={'event_id': self.event.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Katta bayram tadbiri")

    def test_event_registration_flow(self):
        self.client.login(username="event_student", password="password123")
        register_url = reverse('events:event_register', kwargs={'event_id': self.event.id})

        # Register
        res1 = self.client.get(register_url)
        self.assertEqual(res1.status_code, 302)
        self.assertTrue(EventParticipant.objects.filter(event=self.event, user=self.user).exists())

        # Unregister
        res2 = self.client.get(register_url)
        self.assertEqual(res2.status_code, 302)
        self.assertFalse(EventParticipant.objects.filter(event=self.event, user=self.user).exists())
