from django.contrib import admin

from .models import Usuari, InfoImmobiliaria


@admin.register(Usuari)
class UsuariAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'nip', 'is_active', 'is_admin']
    list_filter  = ['is_active', 'is_admin']
    search_fields = ['username', 'email', 'nip']


@admin.register(InfoImmobiliaria)
class InfoImmobiliariaAdmin(admin.ModelAdmin):
    list_display = ['nom_comercial', 'cif', 'email_contacte', 'telefon']
