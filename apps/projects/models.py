from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Qoralama')
        REVIEW = 'REVIEW', _('Ko‘rib chiqilmoqda')
        APPROVED = 'APPROVED', _('Ma‘qullangan')
        IN_PROGRESS = 'IN_PROGRESS', _('Jarayonda')
        COMPLETED = 'COMPLETED', _('Muvaffaqiyatli yakunlangan')
        REJECTED = 'REJECTED', _('Rad etilgan')

    class Category(models.TextChoices):
        IT = 'IT', _('Dasturlash va Axborot Texnologiyalari')
        AUTOMATION = 'AUTOMATION', _('Avtomatlashtirish va Texnika')
        BUSINESS = 'BUSINESS', _('Iqtisodiyot va Buxgalteriya')
        ROBOTICS = 'ROBOTICS', _('Robototexnika va Mexatronika')
        OTHER = 'OTHER', _('Boshqa innovatsion tashabbuslar')

    title = models.CharField(
        max_length=255,
        verbose_name=_('Loyiha / Startap nomi'),
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_projects',
        verbose_name=_('Muallif'),
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_('Tegishli guruh'),
    )
    mentor = models.ForeignKey(
        'teachers.TeacherProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentored_projects',
        verbose_name=_('Ilmiy rahbar / Ustoz'),
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.IT,
        verbose_name=_('Yo‘nalish'),
    )
    description = models.TextField(
        verbose_name=_('Loyiha tavsifi va maqsadi'),
    )
    presentation_file = models.FileField(
        upload_to='projects/presentations/%Y/',
        blank=True,
        null=True,
        verbose_name=_('Taqdimot yoki reja (PDF/PPTX)'),
    )
    project_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('GitHub yoki Veb-sayt havolasi'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REVIEW,
        verbose_name=_('Loyiha holati'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Yaratilgan vaqti'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Yangilangan vaqti'),
    )

    class Meta:
        verbose_name = _('Talabalar loyihasi')
        verbose_name_plural = _('Talabalar loyihalari va startaplari')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ProjectComment(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Loyiha'),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_comments',
        verbose_name=_('Fikr bildiruvchi'),
    )
    comment = models.TextField(
        verbose_name=_('Fikr / Taqriz'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Vaqti'),
    )

    class Meta:
        verbose_name = _('Loyiha muhokamasi fikri')
        verbose_name_plural = _('Loyiha fikrlari')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author}: {self.comment[:30]}"
