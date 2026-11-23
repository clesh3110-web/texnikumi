from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

def role_required(*allowed_roles):
    """
    Foydalanuvchi roli ruxsat etilgan rollar ro'yxatida borligini tekshiradi.
    Foydalanuvchi tizimga kirmagan bo'lsa login sahifasiga yo'naltiradi.
    Roli to'g'ri kelmasa 403 PermissionDenied beradi.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # Superadmin doimo barcha joyga kira oladi
            if request.user.is_superuser or request.user.role == 'superadmin':
                return view_func(request, *args, **kwargs)
                
            if request.user.role not in allowed_roles:
                messages.error(request, "Sizda ushbu sahifaga kirish huquqi mavjud emas!")
                raise PermissionDenied("Sizda ushbu amalni bajarish uchun ruxsat yo'q.")
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Maxsus ruxsat dekoratorlari
superadmin_required = role_required('superadmin')
admin_required = role_required('superadmin', 'admin')
teacher_required = role_required('superadmin', 'admin', 'teacher')
student_required = role_required('superadmin', 'admin', 'student')

class RoleRequiredMixin(AccessMixin):
    """Class-based viewlar uchun rolga asoslangan ruxsat mixini"""
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser or request.user.role == 'superadmin':
            return super().dispatch(request, *args, **kwargs)

        if request.user.role not in self.allowed_roles:
            messages.error(request, "Sizda ushbu sahifaga kirish huquqi mavjud emas!")
            raise PermissionDenied("Sizda ushbu sahifaga kirish ruxsati yo'q.")

        return super().dispatch(request, *args, **kwargs)
