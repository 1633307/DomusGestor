from django.contrib import admin

from .models import Immoble


@admin.register(Immoble)
class ImmobleAdmin(admin.ModelAdmin):
    list_display = ['nom_comercial', 'adreca', 'preu_base_nit', 'capacitat_maxima', 'actiu']
    list_filter = ['actiu']
    search_fields = ['nom_comercial', 'adreca']
