from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class TeacherProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name=_('Foydalanuvchi hisobi')
    )
    department = models.CharField(
        max_length=150,
        default=_('Axborot texnologiyalari kafedrasi'),
        verbose_name=_('Kafedra / Bo‘lim')
    )
    degree = models.CharField(
        max_length=100,
        blank=True,
        default=_('Oliy toifali o‘qituvchi'),
        verbose_name=_('Ilmiy darajasi / Toifasi')
    )
    specialization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Mutaxassisligi')
    )
    office_room = models.CharField(
        max_length=50,
        blank=True,
        default=_('204-xona'),
        verbose_name=_('Xona raqami')
    )
    bio = models.TextField(
        blank=True,
        verbose_name=_('O‘qituvchi haqida qisqacha')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('O‘qituvchi profili')
        verbose_name_plural = _('O‘qituvchilar profillari')
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name_uz} ({self.department})"
