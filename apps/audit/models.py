from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = 'LOGIN', _('Tizimga kirish')
        LOGOUT = 'LOGOUT', _('Tizimdan chiqish')
        GRADE_CHANGE = 'GRADE_CHANGE', _('Baho qo‘yish / tahrirlash')
        ATTENDANCE_CHANGE = 'ATTENDANCE_CHANGE', _('Davomat qayd etish')
        DOCUMENT_VERIFY = 'DOCUMENT_VERIFY', _('Hujjatni tasdiqlash / rad etish')
        USER_CREATE = 'USER_CREATE', _('Foydalanuvchi yaratish')
        SETTINGS_CHANGE = 'SETTINGS_CHANGE', _('Tizim sozlamalari o‘zgarishi')
        OTHER = 'OTHER', _('Boshqa muhim amal')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('Foydalanuvchi'),
    )
    action = models.CharField(
        max_length=30,
        choices=Action.choices,
        default=Action.OTHER,
        verbose_name=_('Harakat turi'),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP manzil'),
    )
    details = models.TextField(
        verbose_name=_('Tafsilotlar'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Vaqti'),
    )

    class Meta:
        verbose_name = _('Audit yozuvi')
        verbose_name_plural = _('Xavfsizlik va audit jurnali')
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.username if self.user else "Anonim"
        return f"[{self.created_at.strftime('%d.%m.%Y %H:%M')}] {user_name} -> {self.get_action_display()}"


def log_audit(user, action, details, ip_address=None):
    """Xavfsizlik audit logiga yangi yozuv qo'shish yordamchi funksiyasi"""
    return AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        details=details,
        ip_address=ip_address
    )
