from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import Message

User = get_user_model()

@login_required
def inbox_view(request):
    """Kiruvchi xabarlar ro'yxati (Section 20)"""
    received_messages = Message.objects.filter(
        recipient=request.user,
        is_deleted_by_recipient=False
    ).select_related('sender')
    
    unread_count = received_messages.filter(is_read=False).count()

    context = {
        'messages_list': received_messages,
        'unread_count': unread_count,
        'folder': 'inbox',
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def sent_view(request):
    """Chiquvchi (yuborilgan) xabarlar ro'yxati"""
    sent_messages = Message.objects.filter(
        sender=request.user,
        is_deleted_by_sender=False
    ).select_related('recipient')

    context = {
        'messages_list': sent_messages,
        'folder': 'sent',
    }
    return render(request, 'messaging/sent.html', context)


@login_required
def compose_view(request):
    """Yangi xabar yozish"""
    reply_to_id = request.GET.get('reply_to')
    prefill_recipient = None
    prefill_subject = ''

    if reply_to_id:
        parent_msg = get_object_or_404(Message, id=reply_to_id)
        prefill_recipient = parent_msg.sender if parent_msg.recipient == request.user else parent_msg.recipient
        prefill_subject = f"Re: {parent_msg.subject}" if not parent_msg.subject.startswith('Re:') else parent_msg.subject

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        attachment = request.FILES.get('attachment')
        parent_id = request.POST.get('parent_message_id')

        if not recipient_id or not subject or not body:
            messages.error(request, "Iltimos, qabul qiluvchi, mavzu va xabar matnini to‘ldiring.")
        else:
            recipient = get_object_or_404(User, id=recipient_id)
            parent = Message.objects.filter(id=parent_id).first() if parent_id else None

            msg = Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                body=body,
                attachment=attachment,
                parent_message=parent,
            )
            messages.success(request, f"{recipient.get_full_name_uz}ga xabar muvaffaqiyatli yuborildi!")
            return redirect('messaging:sent')

    # Xabar yuborish mumkin bo'lgan foydalanuvchilar (O'zidan tashqari faol foydalanuvchilar)
    users = User.objects.filter(is_active=True).exclude(id=request.user.id).order_by('role', 'last_name')

    context = {
        'users': users,
        'prefill_recipient': prefill_recipient,
        'prefill_subject': prefill_subject,
        'reply_to_id': reply_to_id,
    }
    return render(request, 'messaging/compose.html', context)


@login_required
def message_detail_view(request, message_id):
    """Xabar tafsilotlari va unga javob yozish"""
    msg = get_object_or_404(Message.objects.select_related('sender', 'recipient'), id=message_id)

    # Ruxsat tekshirish: faqat yuboruvchi yoki qabul qiluvchi o'qishi mumkin
    if request.user != msg.sender and request.user != msg.recipient:
        raise PermissionDenied("Sizda ushbu xabarni ko‘rish huquqi yo‘q!")

    # Agar qabul qiluvchi o'qiyotgan bo'lsa va hali o'qilmagan bo'lsa
    if request.user == msg.recipient and not msg.is_read:
        msg.is_read = True
        msg.read_at = timezone.now()
        msg.save(update_fields=['is_read', 'read_at'])

    replies = msg.replies.select_related('sender').order_by('created_at')

    context = {
        'message': msg,
        'replies': replies,
    }
    return render(request, 'messaging/detail.html', context)


@login_required
def delete_message_view(request, message_id):
    """Xabarni o'chirish"""
    msg = get_object_or_404(Message, id=message_id)

    if request.user == msg.sender:
        msg.is_deleted_by_sender = True
        msg.save(update_fields=['is_deleted_by_sender'])
    elif request.user == msg.recipient:
        msg.is_deleted_by_recipient = True
        msg.save(update_fields=['is_deleted_by_recipient'])
    else:
        raise PermissionDenied("Ruxsat berilmagan!")

    messages.success(request, "Xabar o‘chirildi.")
    return redirect('messaging:inbox')
