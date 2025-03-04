from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from tinymce.models import HTMLField
from django.utils.text import slugify
from user.models import User, Branch


class SlugifyMixin:
    """Slug generatsiyasi uchun umumiy mixin."""

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class BaseModel(SlugifyMixin, models.Model):
    """Har bir model uchun umumiy bazaviy model."""
    DEGREE_CHOICES = [
        ('LEVEL1', _('Level 1')),
        ('LEVEL2', _('Level 2')),
        ('LEVEL3', _('Level 3')),
    ]

    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE,
        verbose_name=_("Filial"), blank=True, null=True
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name=_("Foydalanuvchi"), blank=True, null=True
    )
    title = models.CharField(max_length=255, verbose_name=_("Mavzu"), blank=True, null=True)
    author = models.CharField(max_length=255, verbose_name=_("Muallif(hammualliflar)"), blank=True, null=True)
    institution_name = models.CharField(max_length=255, verbose_name=_("Muassasa Nomi(kafedra)"), blank=True, null=True)
    keywords = models.CharField(max_length=255, verbose_name=_("Kalit So'zlar"), blank=True, null=True)
    publication_type = models.CharField(max_length=100, verbose_name=_("Nashr turi"), blank=True, null=True)
    publication_year = models.PositiveIntegerField(verbose_name=_("Nashr Yili"), blank=True, null=True)
    description = models.TextField(verbose_name=_("Ilm-fan yo'nalishi"), blank=True, null=True)
    content_type = HTMLField(verbose_name=_("Anotatsiya"), blank=True, null=True)
    degree = models.CharField(max_length=6, choices=DEGREE_CHOICES, verbose_name=_("Daraja"), blank=True, null=True)
    issn_isbn = models.CharField(
        max_length=20, verbose_name=_("ISSN/ISBN"), blank=True, null=True,
        validators=[RegexValidator(r'^\d{4}-\d{4}|\d{9}[\d|X]$', _("ISSN yoki ISBN noto'g'ri formatda"))]
    )
    file = models.FileField(upload_to='files/', verbose_name=_("Fayl"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan Vaqt"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("O'zgartirilgan Vaqt"))
    slug = models.SlugField(max_length=255, verbose_name=_("Alohida qism"), unique=True, null=True)
    image = models.FileField(upload_to='images/', verbose_name=_("Rasm"), blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return self.title or _("Noma'lum")

    def get_absolute_url(self):
        return reverse(f'{self.__class__.__name__.lower()}_detail', args=[self.slug])


class Monografiya(BaseModel):
    class Meta:
        verbose_name = _("Monografiya")
        verbose_name_plural = _("Monografiyalar")


class Risola(BaseModel):
    class Meta:
        verbose_name = _("Risola")
        verbose_name_plural = _("Risolalar")


class Dissertatsiya(BaseModel):
    class Meta:
        verbose_name = _("Dissertatsiya")
        verbose_name_plural = _("Dissertatsiyalar")


class Darslik(BaseModel):
    class Meta:
        verbose_name = _("Darslik")
        verbose_name_plural = _("Darsliklar")


class Loyiha(BaseModel):
    class Meta:
        verbose_name = _("Loyiha")
        verbose_name_plural = _("Loyihalar")


class Jurnal(BaseModel):
    class Meta:
        verbose_name = _("Jurnal")
        verbose_name_plural = _("Jurnallar")


class Maqola(BaseModel):
    class Meta:
        verbose_name = _("Hisobot")
        verbose_name_plural = _("Hisobotlar")


class Xorijiy_Tajriba(models.Model):
    DEGREE_CHOICES = [
        ('LEVEL1', _('Level 1')),
        ('LEVEL2', _('Level 2')),
        ('LEVEL3', _('Level 3')),
    ]
    degree = models.CharField(max_length=6, choices=DEGREE_CHOICES, verbose_name=_("Daraja"))
    title = models.CharField(max_length=255, verbose_name=_("Material mavzusi"))
    author = models.CharField(max_length=255, verbose_name=_("Mualliflar(hammualliflar)"))
    country = models.CharField(max_length=255, verbose_name=_("Mamlakat nomi"))
    Military_organization = models.CharField(max_length=255, verbose_name=_("Harbiy tashkilot"))
    material = models.CharField(max_length=255, verbose_name=_("Material turi"))
    made_in = models.CharField(max_length=255, verbose_name=_("Ishlab chiqardan tashkilot"))
    anotation = models.CharField(max_length=255, verbose_name=_("Anotatsiya"))
    keys = models.CharField(max_length=255, verbose_name=_("Kaliti so'z"))
    file = models.FileField(upload_to='reports_files/', verbose_name=_("Xorijiy_Tajriba Fayli"), blank=True, null=True)
    slug = models.SlugField(max_length=255, verbose_name=_("Alohida qism"), unique=True, null=True)
    image = models.FileField(upload_to='images/', verbose_name=_("Rasm"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Yaratilgan Vaqt"), blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("O'zgartirilgan Vaqt"), blank=True, null=True)

    def __str__(self):
        return self.title


class Qollanma(BaseModel):
    class Meta:
        verbose_name = _("Hisobot")
        verbose_name_plural = _("Hisobotlar")


class Other(BaseModel):
    class Meta:
        verbose_name = _("Boshqalar")
        verbose_name_plural = _("Boshqalar")
