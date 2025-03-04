from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from branch.models import Branch


class UserManager(BaseUserManager):
    def create_user(self, passport_number, username, password, branch=None, **extra_fields):
        """Oddiy foydalanuvchi yaratish"""
        if not passport_number:
            raise ValueError("Pasport raqami kiritish majburiy!")
        if not username:
            raise ValueError("Username kiritish majburiy!")
        if not password:
            raise ValueError("Password kiritish majburiy!")

        user = self.model(passport_number=passport_number, username=username, branch=branch, **extra_fields)
        user.set_password(password)  # Parolni hashlash
        user.user_status = 'waiting'  # Yangi foydalanuvchi kutish rejimida
        user.save(using=self._db)
        return user

    def create_superuser(self, passport_number, username, password, **extra_fields):
        """Superuser yaratish"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'administrator')

        return self.create_user(passport_number, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('administrator', 'Administrator'),
        ('moderator', 'Moderator'),
        ('user1', 'User1'),
        ('user2', 'User2'),
        ('user3', 'User3'),
    ]
    USER_STATUS_CHOICES = [
        ('block', 'Bloklash'),
        ('active', 'Aktivlashtirish'),
        ('waiting', 'Kutib turing'),
    ]

    passport_number = models.CharField(
        max_length=15,
        unique=True,
        db_index=True,
        verbose_name="Pasport Raqami",
    )
    password = models.CharField(
        max_length=255,
        verbose_name="Parol"
    )
    username = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name="Foydalanuvchi Nomi",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faolmi"
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name="Superuser"
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Admin Panelga Kirish Huquqi"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan Vaqt"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name="User Role",
        default='user3',
        db_index=True  # Indeks qo‘shildi, agar filtr qilish kerak bo‘lsa
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        related_name="users",
        verbose_name="Filial",
        null=True,
        blank=True,
        db_index=True
    )
    user_status = models.CharField(
        max_length=10,
        choices=USER_STATUS_CHOICES,
        default='waiting',
        verbose_name="Foydalanuvchi Holati",
        db_index=True  # Indeks qo‘shildi, agar filtr qilish kerak bo‘lsa
    )

    objects = UserManager()

    USERNAME_FIELD = 'passport_number'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.passport_number})"

    def is_active_user(self):
        return self.is_active and self.user_status == 'active'
