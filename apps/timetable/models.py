from django.db import models
from django.utils.translation import gettext_lazy as _

class TimetableItem(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 1, _('Dushanba')
        TUESDAY = 2, _('Seshanba')
        WEDNESDAY = 3, _('Chorshanba')
        THURSDAY = 4, _('Payshanba')
        FRIDAY = 5, _('Juma')
        SATURDAY = 6, _('Shanba')

    LESSON_PAIRS = (
        (1, _('1-juftlik (08:30 - 09:50)')),
        (2, _('2-juftlik (10:00 - 11:20)')),
        (3, _('3-juftlik (11:50 - 13:10)')),
        (4, _('4-juftlik (13:20 - 14:40)')),
        (5, _('5-juftlik (14:50 - 16:10)')),
        (6, _('6-juftlik (16:20 - 17:40)')),
    )

    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='timetable_items',
        verbose_name=_('Guruh'),
    )
    assignment = models.ForeignKey(
        'subjects.TeacherSubjectGroup',
        on_delete=models.CASCADE,
        related_name='timetable_items',
        verbose_name=_('Fan va O‘qituvchi'),
    )
    weekday = models.PositiveSmallIntegerField(
        choices=Weekday.choices,
        verbose_name=_('Hafta kuni'),
    )
    lesson_pair = models.PositiveSmallIntegerField(
        choices=LESSON_PAIRS,
        default=1,
        verbose_name=_('Dars juftligi'),
    )
    room = models.CharField(
        max_length=50,
        default='204-xona',
        verbose_name=_('Xona raqami'),
    )
    start_time = models.TimeField(
        default='08:30',
        verbose_name=_('Boshlanish vaqti'),
    )
    end_time = models.TimeField(
        default='09:50',
        verbose_name=_('Tugash vaqti'),
    )
    academic_year = models.CharField(
        max_length=20,
        default='2024-2025',
        verbose_name=_('O‘quv yili'),
    )
    semester = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('Semestr'),
    )

    class Meta:
        verbose_name = _('Dars jadvali bandi')
        verbose_name_plural = _('Dars jadvallari')
        unique_together = ['group', 'weekday', 'lesson_pair', 'academic_year', 'semester']
        ordering = ['weekday', 'lesson_pair']

    def __str__(self):
        return f"{self.group.name} | {self.get_weekday_display()} [{self.lesson_pair}-juftlik] | {self.assignment.subject.name}"

    @property
    def related_book(self):
        """Ushbu fanga tegishli yuklangan elektron kitob (agar mavjud bo'lsa)"""
        from apps.library.models import Book
        return Book.objects.filter(subject=self.assignment.subject).first()
