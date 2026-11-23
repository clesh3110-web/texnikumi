from django.db import models
from django.utils.translation import gettext_lazy as _

class Subject(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name=_('Fan nomi'),
        db_index=True,
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Fan kodi (Masalan: WEB-201)'),
        db_index=True,
    )
    total_hours = models.PositiveIntegerField(
        default=72,
        verbose_name=_('Jami o‘quv soati'),
    )
    lecture_hours = models.PositiveIntegerField(
        default=36,
        verbose_name=_('Ma‘ruza soatlari'),
    )
    practical_hours = models.PositiveIntegerField(
        default=36,
        verbose_name=_('Amaliyot soatlari'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Fan haqida ma‘lumot'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Faol fan'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Fan')
        verbose_name_plural = _('Fanlar')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class TeacherSubjectGroup(models.Model):
    """
    O'qituvchi, Fan va Guruhni o'zaro bog'lovchi asosiy akademik model.
    Jurnal, davomat va dars jadvallari aynan shu modelga tayanadi.
    """
    teacher = models.ForeignKey(
        'teachers.TeacherProfile',
        on_delete=models.CASCADE,
        related_name='teaching_assignments',
        verbose_name=_('O‘qituvchi'),
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teaching_assignments',
        verbose_name=_('Fan'),
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='teaching_assignments',
        verbose_name=_('Guruh'),
    )
    academic_year = models.CharField(
        max_length=20,
        default='2024-2025',
        verbose_name=_('O‘quv yili'),
    )
    semester = models.PositiveSmallIntegerField(
        default=1,
        choices=((1, _('1-semestr')), (2, _('2-semestr'))),
        verbose_name=_('Semestr'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Faol biriktirish'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('O‘qituvchi-Fan-Guruh biriktiruvi')
        verbose_name_plural = _('O‘qituvchi-Fan-Guruh biriktiruvlari')
        unique_together = ['teacher', 'subject', 'group', 'academic_year', 'semester']
        ordering = ['group__name', 'subject__name']

    def __str__(self):
        return f"{self.group.name} | {self.subject.name} | {self.teacher.user.get_full_name_uz}"
