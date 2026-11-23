from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class Assignment(models.Model):
    assignment = models.ForeignKey(
        'subjects.TeacherSubjectGroup',
        on_delete=models.CASCADE,
        related_name='homework_tasks',
        verbose_name=_('Fan va Guruh biriktiruvi'),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_('Topshiriq nomi'),
    )
    topic = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Dars mavzusi'),
    )
    description = models.TextField(
        verbose_name=_('Topshiriq tavsifi va shartlari'),
    )
    attachment_file = models.FileField(
        upload_to='assignments/tasks/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Biriktirilgan fayl/qo‘llanma'),
    )
    due_date = models.DateTimeField(
        verbose_name=_('Topshirish muddati (Dedlayn)'),
    )
    max_score = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Maksimal baho'),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assignments',
        verbose_name=_('Yaratgan o‘qituvchi'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Uy vazifasi')
        verbose_name_plural = _('Uy vazifalari')
        ordering = ['-due_date', '-created_at']

    def __str__(self):
        return f"{self.assignment.group.name} | {self.assignment.subject.name}: {self.title}"

    @property
    def submissions_count(self):
        return self.submissions.count()

    @property
    def pending_submissions_count(self):
        return self.submissions.filter(status__in=['SUBMITTED', 'REVIEWING']).count()


class AssignmentSubmission(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', _('Yangi')
        SUBMITTED = 'SUBMITTED', _('Yuborilgan')
        REVIEWING = 'REVIEWING', _('Tekshirilmoqda')
        GRADED = 'GRADED', _('Tekshirildi va baholandi')
        REVISE = 'REVISE', _('Qayta ishlash kerak')

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name=_('Topshiriq'),
    )
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
        verbose_name=_('O‘quvchi'),
    )
    submission_text = models.TextField(
        blank=True,
        verbose_name=_('O‘quvchi yozgan javob/izoh'),
    )
    submission_file = models.FileField(
        upload_to='assignments/submissions/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Yechim fayli (PDF/ZIP/Rasm)'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
        verbose_name=_('Tekshiruv holati'),
        db_index=True,
    )
    score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Qo‘yilgan baho (1..5)'),
    )
    teacher_feedback = models.TextField(
        blank=True,
        verbose_name=_('O‘qituvchi taqrizi va izohi'),
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Topshirilgan vazifa')
        verbose_name_plural = _('Topshirilgan vazifalar')
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.user.get_full_name_uz} — {self.assignment.title} ({self.get_status_display()})"
