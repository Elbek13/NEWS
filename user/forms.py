from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.cache import cache
from django.core.exceptions import ValidationError
from .models import User, Branch


def validate_password_strength(value):
    if len(value) < 8:
        raise ValidationError("Parol kamida 8 belgidan iborat bo‘lishi kerak!")
    if not any(char.isdigit() for char in value):
        raise ValidationError("Parolda kamida bitta raqam bo‘lishi kerak!")
    if not any(char.isupper() for char in value):
        raise ValidationError("Parolda kamida bitta katta harf bo‘lishi kerak!")


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Parolni kiriting"
        }),
        label="Parol",
        validators=[validate_password_strength]  # Parol murakkabligini tekshirish
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Parolni qayta kiriting"
        }),
        label="Parolni tasdiqlash"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filiallarni keshdan olish
        cache_key = 'all_branches'
        branches = cache.get(cache_key)
        if not branches:
            branches = Branch.objects.all()
            cache.set(cache_key, branches, 60 * 60)  # 1 soat keshlash
        self.fields['branch'] = forms.ModelChoiceField(
            queryset=branches,
            widget=forms.Select(attrs={
                "class": "form-control",
                "placeholder": "Filialni tanlang"
            }),
            label="Filial",
            empty_label="Filialni tanlang",
            required=False  # Filial ixtiyoriy bo‘lishi mumkin
        )

    class Meta:
        model = User
        fields = ['passport_number', 'username', 'password', 'branch']
        widgets = {
            "passport_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Pasport raqami"
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Foydalanuvchi nomi"
            }),
        }

    def clean_passport_number(self):
        passport_number = self.cleaned_data.get('passport_number')
        if User.objects.filter(passport_number=passport_number).exists():
            raise ValidationError("Bu pasport raqami allaqachon ro‘yxatdan o‘tgan!")
        return passport_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Bu foydalanuvchi nomi allaqachon band!")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Parollar bir xil emas!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Pasport Raqami",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Pasport raqamingizni kiriting"
        })
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Parolni kiriting"
        })
    )


class UserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Parolni kiriting"
        }),
        label="Parol"
    )
    is_active = forms.BooleanField(
        widget=forms.Select(choices=((True, 'Ha'), (False, 'Yo‘q')), attrs={"class": "form-select"}),
        label="Faolmi?",
        required=False
    )
    is_staff = forms.BooleanField(
        widget=forms.Select(choices=((True, 'Ha'), (False, 'Yo‘q')), attrs={"class": "form-select"}),
        label="Admin panelga kira oladimi?",
        required=False
    )
    is_superuser = forms.BooleanField(
        widget=forms.Select(choices=((True, 'Ha'), (False, 'Yo‘q')), attrs={"class": "form-select"}),
        label="Superuser?",
        required=False
    )

    class Meta:
        model = User
        fields = [
            'passport_number', 'username', 'password', 'role', 'branch', 'user_status',
            'is_active', 'is_staff', 'is_superuser'
        ]
        widgets = {
            "passport_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Pasport raqami"
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Foydalanuvchi nomi"
            }),
            "role": forms.Select(attrs={"class": "form-select"}),
            "user_status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Joriy foydalanuvchi
        super().__init__(*args, **kwargs)

        # Barcha maydonlarni ixtiyoriy qilish
        for field in self.fields:
            self.fields[field].required = False

        # Branch maydonini keshdan olish
        cache_key = 'all_branches'
        branches = cache.get(cache_key)
        if not branches:
            branches = Branch.objects.all()
            cache.set(cache_key, branches, 60 * 60)  # 1 soat kesh

        self.fields['branch'] = forms.ModelChoiceField(
            queryset=branches,
            widget=forms.Select(attrs={"class": "form-select"}),
            label="Filial",
            empty_label="Filial tanlang",
            required=False
        )

        # Moderator uchun branch cheklovi
        if isinstance(user, User) and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['disabled'] = True

    def clean_passport_number(self):
        passport_number = self.cleaned_data.get('passport_number')
        if passport_number and User.objects.exclude(pk=self.instance.pk).filter(
                passport_number=passport_number).exists():
            raise forms.ValidationError("Bu pasport raqami allaqachon band!")
        return passport_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise forms.ValidationError("Bu foydalanuvchi nomi allaqachon band!")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        elif user.pk:  # Agar foydalanuvchi mavjud bo‘lsa, eski parolni saqlash
            user.password = User.objects.get(pk=user.pk).password
        if commit:
            user.save()
        return user
