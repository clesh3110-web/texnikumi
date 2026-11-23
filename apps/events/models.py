from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Event(models.Model):
    title = models.CharField(
        max_length=250,
        verbose_name=_('Tadbir nomi'),
    )
    description = models.TextField(
        verbose_name=_('Tadbir haqida batafsil ma‘lumot'),
    )
    event_date = models.DateTimeField(
        verbose_name=_('O‘tkazilish vaqti'),
    )
    location = models.CharField(
        max_length=200,
        verbose_name=_('O‘tkazilish joyi (xona / zal)'),
    )
    organizer = models.CharField(
        max_length=200,
        verbose_name=_('Tashkilotchi'),
    )
    banner_image = models.ImageField(
        upload_to='events/banners/%Y/',
        blank=True,
        null=True,
        verbose_name=_('Afisha / Banner'),
    )
    max_participants = models.PositiveIntegerField(
        default=100,
        verbose_name=_('Maksimal qatnashuvchilar soni'),
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Barcha uchun ochiq'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Yaratilgan vaqti'),
    )

    class Meta:
        verbose_name = _('Tadbir / Bayram')
        verbose_name_plural = _('Tadbirlar va bayramlar')
        ordering = ['-event_date']

    def __str__(self):
        return self.title

    @property
    def participants_count(self):
        return self.participants.count()


class EventParticipant(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name=_('Tadbir'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        verbose_name=_('Qatnashuvchi'),
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Ro‘yxatdan o‘tgan vaqti'),
    )

    class Meta:
        verbose_name = _('Tadbir qatnashuvchisi')
        verbose_name_plural = _('Tadbir qatnashuvchilari')
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.get_full_name_uz} — {self.event.title}"
