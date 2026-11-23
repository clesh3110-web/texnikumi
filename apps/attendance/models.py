from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', _('Darsda')
        LATE = 'LATE', _('Kechikdi')
        SICK = 'SICK', _('Kasallik sababli kelmadi')
        ABSENT = 'ABSENT', _('Boshqa sabab bilan kelmadi')

    LESSON_PAIRS = (
        (1, _('1-juftlik (08:30 - 09:50)')),
        (2, _('2-juftlik (10:00 - 11:20)')),
        (3, _('3-juftlik (11:50 - 13:10)')),
        (4, _('4-juftlik (13:20 - 14:40)')),
        (5, _('5-juftlik (14:50 - 16:10)')),
        (6, _('6-juftlik (16:20 - 17:40)')),
    )

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('O‘quvchi'),
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('Guruhi'),
    )
    date = models.DateField(
        verbose_name=_('Sana'),
        db_index=True,
    )
    lesson_pair = models.PositiveSmallIntegerField(
        choices=LESSON_PAIRS,
        default=1,
        verbose_name=_('Dars juftligi'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
        verbose_name=_('Davomat holati'),
        db_index=True,
    )
    assignment = models.ForeignKey(
        'subjects.TeacherSubjectGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances',
        verbose_name=_('Fan biriktiruvi'),
    )
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances',
        verbose_name=_('Belgilagan xodim'),
    )
    comment = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Qo‘shimcha izoh'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Davomat yozuvi')
        verbose_name_plural = _('Davomat yozuvlari')
        unique_together = ['student', 'date', 'lesson_pair']
        ordering = ['-date', 'lesson_pair', 'student__user__last_name']

    def __str__(self):
        return f"{self.date} [{self.lesson_pair}-juftlik] {self.student.user.get_full_name_uz}: {self.get_status_display()}"
