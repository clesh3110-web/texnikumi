from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Notification

@login_required
def notifications_list_view(request):
    """Foydalanuvchining barcha bildirishnomalari (Section 23)"""
    notifs = Notification.objects.filter(recipient=request.user)
    unread_count = notifs.filter(is_read=False).count()

    context = {
        'notifications': notifs,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notifications_list.html', context)


@login_required
def mark_as_read_view(request, notif_id):
    """Bildirishnomani o'qilgan deb belgilash va uning havolasiga o'tish"""
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save(update_fields=['is_read'])

    if notif.link_url:
        return redirect(notif.link_url)
    return redirect('notifications:notifications_list')


@login_required
def mark_all_read_view(request):
    """Barcha bildirishnomalarni birdaniga o'qilgan deb belgilash"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Barcha bildirishnomalar o‘qilgan deb belgilandi.")
    return redirect('notifications:notifications_list')


@login_required
def unread_count_api(request):
    """Navbar-dagi qo'ng'iroqcha (bell icon) uchun real-time unread count API"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})
