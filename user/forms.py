from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Branch


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Parolni kiriting"
        }),
        label="Parol"
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        widget=forms.Select(attrs={
            "class": "form-control",
            "placeholder": "Filialni tanlang"
        }),
        label="Filial"
    )

    class Meta:
        model = User
        fields = ['passport_number', 'username', 'password', 'branch']
        widgets = {
            "passport_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Pasport raqami"}),
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Foydalanuvchi nomi"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Parolni hash qilish
        user.user_status = 'waiting'  # Admin tasdiqlashini kutish rejimi
        user.is_active = False  # Foydalanuvchi faqat admin tasdiqlagandan keyin kira oladi
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
    # Maydonlar
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Parolni kiriting"
        }),
        label="Parol"
    )
    is_active = forms.ChoiceField(
        choices=((True, 'Ha'), (False, 'Yo‘q')),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Faolmi?",
        required=False
    )
    is_staff = forms.ChoiceField(
        choices=((True, 'Ha'), (False, 'Yo‘q')),
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Admin panelga kira oladimi?",
        required=False
    )
    is_superuser = forms.ChoiceField(
        choices=((True, 'Ha'), (False, 'Yo‘q')),
        widget=forms.Select(attrs={"class": "form-select"}),
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
            "branch": forms.Select(attrs={"class": "form-select"}),
            "user_status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Barcha maydonlarni ixtiyoriy qilish
        for field in self.fields:
            self.fields[field].required = False

        # Moderator uchun branch cheklovi
        if isinstance(user, User) and user.role == 'moderator' and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(id=user.branch.id)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].disabled = True
        else:
            self.fields['branch'].queryset = Branch.objects.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        elif user.pk:  # Agar foydalanuvchi allaqachon mavjud bo‘lsa
            user.password = User.objects.get(pk=user.pk).password
        if commit:
            user.save()
        return user
