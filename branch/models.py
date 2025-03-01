from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100, verbose_name="Filial Nomi", unique=True)  # Filial nomini yagona qilish uchun `unique=True` qo'shildi
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan Vaqt")

    def __str__(self):
        return self.name