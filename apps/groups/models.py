from django.db import models
from django.utils.translation import gettext_lazy as _

class Group(models.Model):
    class Course(models.IntegerChoices):
        FIRST = 1, _('1-kurs')
        SECOND = 2, _('2-kurs')
        THIRD = 3, _('3-kurs')

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Guruh nomi (Masalan: DI-21, AT-22)'),
        db_index=True,
    )
    course = models.PositiveSmallIntegerField(
        choices=Course.choices,
        default=Course.FIRST,
        verbose_name=_('Kurs'),
    )
    direction = models.CharField(
        max_length=200,
        verbose_name=_('Ta‘lim yo‘nalishi / Mutaxassislik'),
        default=_('Dasturiy injiniring'),
    )
    academic_year = models.CharField(
        max_length=20,
        default='2024-2025',
        verbose_name=_('O‘quv yili'),
    )
    curator = models.ForeignKey(
        'teachers.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='curated_groups',
        verbose_name=_('Guruh rahbari (Kurator)'),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Faol guruh'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Guruh')
        verbose_name_plural = _('Guruhlar')
        ordering = ['course', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_course_display()})"

    @property
    def total_students_count(self):
        """Guruhdagi jami o'quvchilar soni"""
        return self.students.count()

    @property
    def active_students_count(self):
        """Hozir o'qiyotgan faol o'quvchilar soni"""
        return self.students.filter(status='ACTIVE').count()
