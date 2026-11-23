from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class LoginForm(forms.Form):
    """
    Moslashuvchan tizimga kirish formasi:
    Foydalanuvchi login (username), telefon raqam yoki email orqali kira oladi.
    """
    login_field = forms.CharField(
        label=_("Login, Telefon yoki Email"),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Login, +998901234567 yoki email',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label=_("Parol"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Parolingizni kiriting',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Eslab qolish"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        login_input = cleaned_data.get('login_field')
        password = cleaned_data.get('password')

        if login_input and password:
            # Login, telefon yoki email bo'yicha foydalanuvchini topish
            user = None
            try:
                if '@' in login_input:
                    user_obj = User.objects.filter(email__iexact=login_input).first()
                elif login_input.startswith('+') or login_input.isdigit():
                    user_obj = User.objects.filter(phone=login_input).first()
                else:
                    user_obj = User.objects.filter(username__iexact=login_input).first()

                if user_obj:
                    user = authenticate(username=user_obj.username, password=password)
            except Exception:
                user = None

            if user is None:
                raise forms.ValidationError(
                    _("Kiritilgan login yoki parol noto‘g‘ri. Iltimos, qaytadan tekshirib ko‘ring.")
                )
            if not user.is_active:
                raise forms.ValidationError(
                    _("Ushbu hisob faolsizlantirilgan. Administrator bilan bog‘laning.")
                )
            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)


class UserProfileForm(forms.ModelForm):
    """Foydalanuvchi shaxsiy ma'lumotlarini tahrirlash formasi"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email', 'avatar', 'address', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
