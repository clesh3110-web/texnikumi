from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Book(models.Model):
    title = models.CharField(
        max_length=250,
        verbose_name=_('Kitob nomi'),
        db_index=True,
    )
    author = models.CharField(
        max_length=200,
        verbose_name=_('Muallif(lar)'),
        db_index=True,
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name=_('Tegishli fan'),
    )
    isbn = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('ISBN / Kod'),
    )
    published_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Nashr yili'),
    )
    cover_image = models.ImageField(
        upload_to='library/covers/%Y/',
        blank=True,
        null=True,
        verbose_name=_('Kitob muqovasi'),
    )
    pdf_file = models.FileField(
        upload_to='library/books/%Y/',
        verbose_name=_('Elektron kitob (PDF)'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Kitob haqida qisqacha tavsif'),
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Ko‘rishlar soni'),
    )
    downloads_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Yuklab olishlar soni'),
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Barcha uchun ochiq'),
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Yuklagan foydalanuvchi'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Elektron kitob')
        verbose_name_plural = _('Elektron kutubxona kitoblari')
        ordering = ['title']

    def __str__(self):
        return f"{self.title} — {self.author}"


class BookRequest(models.Model):
    """
    Dars jadvalidagi fan nomini bosganda kitob bo'lmasa,
    o'quvchi yuborishi mumkin bo'lgan kitob so'rovi (Section 17 & 18).
    """
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='book_requests',
        verbose_name=_('O‘quvchi'),
    )
    subject = models.ForeignKey(
        'subjects.Subject',
        on_delete=models.CASCADE,
        related_name='book_requests',
        verbose_name=_('Fan'),
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('Izoh yoki talab'),
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name=_('Kitob yuklandi / Hal qilindi'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Kitob so‘rovi')
        verbose_name_plural = _('Kitob so‘rovlari')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.get_full_name_uz} — {self.subject.name} (Kitob so‘rovi)"
