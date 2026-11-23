from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = 'superadmin', _('Super Administrator')
        ADMIN = 'admin', _('Administrator')
        TEACHER = 'teacher', _('O‘qituvchi')
        STUDENT = 'student', _('O‘quvchi')

    class Gender(models.TextChoices):
        MALE = 'M', _('Erkak')
        FEMALE = 'F', _('Ayol')

    # Asosiy rol
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('Foydalanuvchi roli'),
        db_index=True,
    )

    # Shaxsiy qo'shimcha ma'lumotlar
    middle_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('Otasining ismi (Sharifi)'),
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('Telefon raqami'),
    )
    jshshir = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name=_('JSHSHIR (PINFL)'),
        help_text=_('14 ta raqamdan iborat shaxsiy identifikatsiya raqami'),
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Profil fotosurati'),
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Tug‘ilgan sana'),
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True,
        verbose_name=_('Jinsi'),
    )
    address = models.TextField(
        blank=True,
        verbose_name=_('Yashash manzili'),
    )
    is_verified = models.BooleanField(
        default=True,
        verbose_name=_('Tasdiqlangan holati'),
    )

    class Meta:
        verbose_name = _('Foydalanuvchi')
        verbose_name_plural = _('Foydalanuvchilar')
        ordering = ['-date_joined']

    def __str__(self):
        full_name = self.get_full_name_uz
        if full_name:
            return f"{full_name} ({self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"

    @property
    def get_full_name_uz(self):
        """O'zbekcha to'liq ism: Familiya Ism Sharifi"""
        parts = [self.last_name, self.first_name, self.middle_name]
        return " ".join([p for p in parts if p]).strip()

    @property
    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN or self.is_superuser

    @property
    def is_admin_user(self):
        return self.role in [self.Role.SUPERADMIN, self.Role.ADMIN]

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def save(self, *args, **kwargs):
        # Superadmin uchun is_staff va is_superuser avtomatik belgilash
        if self.role == self.Role.SUPERADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.role == self.Role.ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)
