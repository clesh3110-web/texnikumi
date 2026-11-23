from django.db import models
from django.utils.translation import gettext_lazy as _

class News(models.Model):
    title = models.CharField(max_length=250, verbose_name=_('Yangilik sarlavhasi'))
    summary = models.TextField(verbose_name=_('Qisqacha mazmuni'))
    content = models.TextField(verbose_name=_('Batafsil matni'))
    image = models.ImageField(upload_to='news/%Y/%m/', blank=True, null=True, verbose_name=_('Asosiy rasm'))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_('Ko‘rishlar soni'))
    is_published = models.BooleanField(default=True, verbose_name=_('Saytda chop etilgan'))
    published_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Chop etilgan sana'))

    class Meta:
        verbose_name = _('Yangilik')
        verbose_name_plural = _('Yangiliklar')
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Announcement(models.Model):
    title = models.CharField(max_length=250, verbose_name=_('E‘lon sarlavhasi'))
    description = models.TextField(verbose_name=_('Batafsil tavsifi'))
    event_date = models.DateField(blank=True, null=True, verbose_name=_('Tadbir/Muddat sanasi'))
    is_urgent = models.BooleanField(default=False, verbose_name=_('Muhim e‘lon'))
    is_active = models.BooleanField(default=True, verbose_name=_('Faol e‘lon'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('E‘lon')
        verbose_name_plural = _('E‘lonlar')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Leadership(models.Model):
    full_name = models.CharField(max_length=150, verbose_name=_('F.I.Sh'))
    position = models.CharField(max_length=150, verbose_name=_('Lavozimi'))
    photo = models.ImageField(upload_to='leadership/', blank=True, null=True, verbose_name=_('Surati'))
    phone = models.CharField(max_length=50, blank=True, verbose_name=_('Telefon raqami'))
    email = models.EmailField(blank=True, verbose_name=_('Elektron pochta'))
    reception_days = models.CharField(max_length=150, default='Dushanba - Juma, 14:00 - 17:00', verbose_name=_('Qabul kunlari'))
    order = models.PositiveSmallIntegerField(default=0, verbose_name=_('Tartib raqami'))

    class Meta:
        verbose_name = _('Rahbariyat xodimi')
        verbose_name_plural = _('Rahbariyat')
        ordering = ['order', 'full_name']

    def __str__(self):
        return f"{self.full_name} — {self.position}"


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150, verbose_name=_('F.I.Sh'))
    phone = models.CharField(max_length=30, verbose_name=_('Telefon raqam'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    subject = models.CharField(max_length=200, verbose_name=_('Murojaat mavzusi'))
    message = models.TextField(verbose_name=_('Murojaat matni'))
    is_read = models.BooleanField(default=False, verbose_name=_('O‘qilgan'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Murojaat')
        verbose_name_plural = _('Murojaatlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.subject}"
