from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class StudentProfile(models.Model):
    class EducationType(models.TextChoices):
        GRANT = 'GRANT', _('Davlat granti')
        CONTRACT = 'CONTRACT', _('To‘lov-shartnoma')

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('O‘qimoqda')
        ACADEMIC_LEAVE = 'LEAVE', _('Akademik ta‘tilda')
        EXPELLED = 'EXPELLED', _('Chetlashtirilgan')
        GRADUATED = 'GRADUATED', _('Bitirgan')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name=_('Foydalanuvchi hisobi')
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name=_('Guruhi')
    )
    student_id_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('Talaba ID / Guvohnoma raqami')
    )
    education_type = models.CharField(
        max_length=20,
        choices=EducationType.choices,
        default=EducationType.GRANT,
        verbose_name=_('Ta‘lim shakli')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('O‘qish holati')
    )
    enrollment_year = models.PositiveIntegerField(
        default=2024,
        verbose_name=_('Qabul qilingan yili')
    )
    parent_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Ota-onasining F.I.Sh')
    )
    parent_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Ota-onasining telefon raqami')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('O‘quvchi profili')
        verbose_name_plural = _('O‘quvchilar profillari')
        ordering = ['group__name', 'user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name_uz} — {self.group.name if self.group else 'Guruhsiz'}"

    @property
    def full_name(self):
        return self.user.get_full_name_uz

    @property
    def gpa(self):
        from apps.journal.models import Grade
        from django.db.models import Avg
        avg = Grade.objects.filter(student=self).aggregate(Avg('score'))['score__avg']
        return round(avg, 2) if avg is not None else 0.0

    @property
    def attendance_percentage(self):
        from apps.attendance.models import Attendance
        records = Attendance.objects.filter(student=self)
        total = records.count()
        if total == 0:
            return 0.0
        present = records.filter(status__in=[Attendance.Status.PRESENT, Attendance.Status.LATE]).count()
        return round((present / total) * 100, 1)
