from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import LoginForm, UserProfileForm
from .models import User

def login_view(request):
    """Foydalanuvchini autentifikatsiya qilish va tizimga kiritish"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Eslab qolish sozlamasi
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Brauzer yopilganda sessiya tugaydi
            else:
                request.session.set_expiry(1209600)  # 2 hafta saqlanadi

            messages.success(request, f"Xush kelibsiz, {user.get_full_name_uz or user.username}!")
            
            # Keyingi yo'naltiriladigan manzil
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)

            return redirect('accounts:dashboard_redirect')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Tizimdan xavfsiz chiqish"""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Siz tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('accounts:login')


@login_required
def dashboard_redirect_view(request):
    """
    Foydalanuvchi roliga qarab tegishli panelga yo'naltirish.
    """
    user = request.user
    if user.is_superadmin or user.is_admin_user:
        return redirect('core:admin_dashboard')
    elif user.is_teacher:
        return redirect('teachers:teacher_dashboard')
    elif user.is_student:
        return redirect('students:student_dashboard')
    else:
        return redirect('accounts:profile')


@login_required
def profile_view(request):
    """Foydalanuvchining shaxsiy kabinet profili"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Shaxsiy ma'lumotlaringiz muvaffaqiyatli yangilandi!")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)
