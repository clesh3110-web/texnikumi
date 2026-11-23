from django.shortcuts import render
from django.db.models import Q
from apps.accounts.permissions import admin_required
from .models import AuditLog

@admin_required
def audit_log_view(request):
    """Administratorlar uchun Xavfsizlik va Audit jurnali (Section 25)"""
    query = request.GET.get('q', '').strip()
    action = request.GET.get('action', '')

    logs = AuditLog.objects.select_related('user').all()

    if query:
        logs = logs.filter(
            Q(details__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(ip_address__icontains=query)
        )

    if action:
        logs = logs.filter(action=action)

    context = {
        'logs': logs[:100], # So'nggi 100 ta amal
        'actions': AuditLog.Action.choices,
        'selected_action': action,
        'query': query,
        'total_count': logs.count(),
    }
    return render(request, 'audit/audit_log.html', context)
