from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    class Type(models.TextChoices):
        INFO = 'INFO', _('Umumiy ma‘lumot')
        GRADE = 'GRADE', _('Yangi baho')
        ATTENDANCE = 'ATTENDANCE', _('Davomat qaydi')
        ASSIGNMENT = 'ASSIGNMENT', _('Uy vazifasi')
        MESSAGE = 'MESSAGE', _('Yangi xabar')
        SYSTEM = 'SYSTEM', _('Tizim xabarnomasi')

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Qabul qiluvchi'),
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Sarlavha'),
    )
    message = models.TextField(
        verbose_name=_('Xabarnoma matni'),
    )
    link_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('O‘tish havolasi'),
    )
    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.INFO,
        verbose_name=_('Turi'),
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('O‘qilgan'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Vaqti'),
    )

    class Meta:
        verbose_name = _('Bildirishnoma')
        verbose_name_plural = _('Bildirishnomalar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username}: {self.title}"
