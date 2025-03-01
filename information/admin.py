from django.contrib import admin
from .models import (
    Monografiya, Risola, Dissertatsiya, Darslik, Loyiha, Jurnal, Maqola, Xorijiy_Tajriba, Qollanma, Other
)


@admin.register(Monografiya)
class MonografiyaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Risola)
class RisolaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Dissertatsiya)
class DissertatsiyaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Darslik)
class DarslikAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Loyiha)
class LoyihaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Jurnal)
class JurnalAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Maqola)
class MaqolaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Xorijiy_Tajriba)
class XorijiyTajribaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'country', 'Military_organization', 'made_in')
    list_filter = ('country', 'Military_organization', 'made_in')
    search_fields = ('title', 'author', 'keys')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Qollanma)
class QollanmaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Other)
class OtherAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_year', 'branch', 'user')
    list_filter = ('branch', 'publication_year')
    search_fields = ('title', 'author', 'keywords')
    prepopulated_fields = {'slug': ('title',)}