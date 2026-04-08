from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuari, Propietari, InfoImmobiliaria


@admin.register(Usuari)
class UsuariAdmin(UserAdmin):
    list_display = ['username', 'email', 'nip', 'rol', 'is_active']
    list_filter = ['rol', 'is_active']
    search_fields = ['username', 'email', 'nip']
    fieldsets = UserAdmin.fieldsets + (
        ('DomusGestor', {'fields': ('nip', 'rol')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('DomusGestor', {'fields': ('nip', 'rol', 'email')}),
    )


@admin.register(Propietari)
class PropietariAdmin(admin.ModelAdmin):
    list_display = ['nom', 'dni_nie', 'email']
    search_fields = ['nom', 'dni_nie', 'email']


@admin.register(InfoImmobiliaria)
class InfoImmobiliariaAdmin(admin.ModelAdmin):
    list_display = ['nom_comercial', 'cif', 'email_contacte']
