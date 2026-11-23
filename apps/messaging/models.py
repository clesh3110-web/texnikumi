from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('Yuboruvchi'),
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('Qabul qiluvchi'),
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('Mavzu'),
    )
    body = models.TextField(
        verbose_name=_('Xabar matni'),
    )
    attachment = models.FileField(
        upload_to='messages/attachments/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Biriktirilgan fayl'),
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('O‘qilgan'),
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('O‘qilgan vaqti'),
    )
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('Javob yozilgan xabar'),
    )
    is_deleted_by_sender = models.BooleanField(
        default=False,
        verbose_name=_('Yuboruvchi tomonidan o‘chirilgan'),
    )
    is_deleted_by_recipient = models.BooleanField(
        default=False,
        verbose_name=_('Qabul qiluvchi tomonidan o‘chirilgan'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Yuborilgan vaqti'),
    )

    class Meta:
        verbose_name = _('Ichki xabar')
        verbose_name_plural = _('Ichki xabarlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.subject[:30]}"
