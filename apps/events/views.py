from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, EventParticipant

def events_list_view(request):
    """Tadbirlar ro'yxati (Section 21)"""
    upcoming_events = Event.objects.filter(is_public=True, event_date__gte=timezone.now()).order_by('event_date')
    past_events = Event.objects.filter(is_public=True, event_date__lt=timezone.now()).order_by('-event_date')[:10]

    # Agar login qilgan bo'lsa, qaysi tadbirlarga yozilganini belgilaymiz
    user_event_ids = set()
    if request.user.is_authenticated:
        user_event_ids = set(request.user.event_registrations.values_list('event_id', flat=True))

    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'user_event_ids': user_event_ids,
    }
    return render(request, 'events/event_list.html', context)


def event_detail_view(request, event_id):
    """Tadbir tafsilotlari va ishtirokchilar"""
    event = get_object_or_404(Event, id=event_id)
    is_registered = False

    if request.user.is_authenticated:
        is_registered = EventParticipant.objects.filter(event=event, user=request.user).exists()

    participants = event.participants.select_related('user')[:30]

    context = {
        'event': event,
        'is_registered': is_registered,
        'participants': participants,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def event_register_view(request, event_id):
    """Tadbirga qatnashish uchun ro'yxatdan o'tish yoki bekor qilish"""
    event = get_object_or_404(Event, id=event_id)

    registration = EventParticipant.objects.filter(event=event, user=request.user).first()
    if registration:
        registration.delete()
        messages.info(request, f"'{event.title}' tadbiriga ishtirokingiz bekor qilindi.")
    else:
        if event.participants.count() >= event.max_participants:
            messages.error(request, "Afsuski, ushbu tadbir uchun barcha o‘rinlar band qilingan!")
        else:
            EventParticipant.objects.create(event=event, user=request.user)
            messages.success(request, f"'{event.title}' tadbiriga muvaffaqiyatli ro‘yxatdan o‘tdingiz!")

    return redirect('events:event_detail', event_id=event.id)
