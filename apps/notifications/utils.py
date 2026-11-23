from .models import Notification

def send_notification(recipient, title, message, link_url='', notification_type=Notification.Type.INFO):
    """Foydalanuvchiga tizim ichki bildirishnomasini yuborish yordamchi funksiyasi"""
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        link_url=link_url,
        notification_type=notification_type
    )
