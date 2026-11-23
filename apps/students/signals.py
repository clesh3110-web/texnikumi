from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import User
from .models import StudentProfile

@receiver(post_save, sender=User)
def create_or_update_student_profile(sender, instance, created, **kwargs):
    if instance.role == User.Role.STUDENT:
        StudentProfile.objects.get_or_create(user=instance)
