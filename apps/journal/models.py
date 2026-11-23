from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Grade(models.Model):
    class GradeType(models.TextChoices):
        CURRENT = 'CURRENT', _('Joriy baho')
        MIDTERM = 'MIDTERM', _('Oraliq nazorat')
        FINAL = 'FINAL', _('Yakuniy nazorat')
        HOMEWORK = 'HOMEWORK', _('Uy vazifasi')
        ACTIVITY = 'ACTIVITY', _('Darsdagi faollik')

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_('O‘quvchi'),
    )
    assignment = models.ForeignKey(
        'subjects.TeacherSubjectGroup',
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_('Fan va O‘qituvchi biriktiruvi'),
    )
    lesson_date = models.DateField(
        verbose_name=_('Dars sanasi'),
        db_index=True,
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Baho (1 dan 5 gacha)'),
    )
    grade_type = models.CharField(
        max_length=20,
        choices=GradeType.choices,
        default=GradeType.CURRENT,
        verbose_name=_('Baho turi'),
    )
    topic = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Dars mavzusi'),
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('O‘qituvchi izohi'),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='given_grades',
        verbose_name=_('Baholagan o‘qituvchi'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Baho')
        verbose_name_plural = _('Baholar')
        ordering = ['-lesson_date', '-id']

    def __str__(self):
        return f"{self.student.user.get_full_name_uz} — {self.assignment.subject.name}: {self.score} ball ({self.get_grade_type_display()})"


class GradeAuditLog(models.Model):
    """
    Baholash tizimi auditi: Kim, qachon va nima uchun bahoni o'zgartirganini qayd etadi.
    """
    grade = models.ForeignKey(
        Grade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_('Baho yozuvi'),
    )
    student_name = models.CharField(max_length=200, verbose_name=_('O‘quvchi'))
    subject_name = models.CharField(max_length=200, verbose_name=_('Fan'))
    old_score = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Eski baho'))
    new_score = models.PositiveSmallIntegerField(verbose_name=_('Yangi baho'))
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('O‘zgartirgan xodim'),
    )
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('O‘zgartirilgan vaqt'))
    reason = models.TextField(blank=True, verbose_name=_('O‘zgartirish sababi'))

    class Meta:
        verbose_name = _('Baho o‘zgarish auditi')
        verbose_name_plural = _('Baholar auditi jurnali')
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.student_name} | {self.old_score} -> {self.new_score} ({self.changed_by})"
