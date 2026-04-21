from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuari, InfoImmobiliaria


@admin.register(Usuari)
class UsuariAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('DomusGestor', {'fields': ('nip',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('DomusGestor', {'fields': ('nip', 'email')}),
    )


@admin.register(InfoImmobiliaria)
class InfoImmobiliariaAdmin(admin.ModelAdmin):
    list_display = ['nom_comercial', 'cif', 'email_contacte', 'telefon']
