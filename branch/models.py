from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100, verbose_name="Filial Nomi", unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan Vaqt")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # yoki ['-created_at'] (eng yangi birinchi)