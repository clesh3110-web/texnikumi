import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_document_file(value):
    """Fayl xavfsizligi: faqat PDF, JPG, PNG va hajmi 5MB dan oshmasligi kerak"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if ext not in valid_extensions:
        raise ValidationError(_("Faqat PDF, JPG yoki PNG formatidagi fayllarni yuklash mumkin!"))
    if value.size > 5 * 1024 * 1024:
        raise ValidationError(_("Fayl hajmi 5 MB dan oshmasligi kerak!"))


class AttendanceDocument(models.Model):
    class DocType(models.TextChoices):
        SPRAVKA = 'SPRAVKA', _('Tibbiy ma‘lumotnoma (095/h spravka)')
        EXPLANATION = 'EXPLANATION', _('Tushuntirish xati')

    class Status(models.TextChoices):
        NEW = 'NEW', _('Yangi')
        REVIEWING = 'REVIEWING', _('Tekshirilmoqda')
        APPROVED = 'APPROVED', _('Tasdiqlangan')
        REJECTED = 'REJECTED', _('Rad etilgan')

    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='attendance_documents',
        verbose_name=_('O‘quvchi'),
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='attendance_documents',
        verbose_name=_('Guruhi'),
    )
    doc_type = models.CharField(
        max_length=20,
        choices=DocType.choices,
        default=DocType.SPRAVKA,
        verbose_name=_('Hujjat turi'),
    )
    start_date = models.DateField(
        verbose_name=_('Kelmagan boshlanish sanasi'),
    )
    end_date = models.DateField(
        verbose_name=_('Tugash sanasi'),
    )
    reason = models.TextField(
        verbose_name=_('Kelmaslik sababi'),
    )
    file = models.FileField(
        upload_to='attendance_documents/%Y/%m/',
        validators=[validate_document_file],
        verbose_name=_('Yuklangan fayl (PDF/Rasm)'),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name=_('Tekshiruv holati'),
        db_index=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_documents',
        verbose_name=_('Tekshirgan xodim'),
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Tekshirilgan sana'),
    )
    review_comment = models.TextField(
        blank=True,
        verbose_name=_('Tekshiruvchi izohi'),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Davomat hujjati')
        verbose_name_plural = _('Davomat hujjatlari (Spravkalar)')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.get_full_name_uz} — {self.get_doc_type_display()} ({self.start_date} - {self.end_date})"

    def can_user_access(self, user):
        """
        XAVFSIZLIK: Tibbiy ma'lumotlar maxfiy!
        Faqat o'quvchining o'zi, uning guruh rahbari va ma'muriyat ko'ra oladi.
        """
        if user.is_superuser or user.is_admin_user:
            return True
        if hasattr(user, 'student_profile') and self.student == user.student_profile:
            return True
        if hasattr(user, 'teacher_profile') and self.group.curator == user.teacher_profile:
            return True
        return False
