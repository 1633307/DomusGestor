from django.contrib import admin
from .models import Immoble, Temporada


class TemporadaInline(admin.TabularInline):
    model = Temporada
    extra = 0


@admin.register(Immoble)
class ImmobleAdmin(admin.ModelAdmin):
    list_display = ['nom_comercial', 'adreca', 'preu_base', 'actiu', 'estat_neteja']
    list_filter = ['actiu', 'estat_neteja']
    search_fields = ['nom_comercial', 'adreca']
    inlines = [TemporadaInline]


@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    list_display = ['nom_descriptiu', 'immoble', 'data_inici', 'data_fi', 'preu_nit']
    list_filter = ['nom_descriptiu']
