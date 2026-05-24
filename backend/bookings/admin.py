from django.contrib import admin

from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Hoste, Comunicacio, ComunicacioEmail


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'email', 'telefon', 'nacionalitat', 'es_inquili', 'es_propietari']
    search_fields = ['nom_complet', 'email', 'telefon', 'dni_passaport']

    @admin.display(boolean=True)
    def es_inquili(self, obj):
        return hasattr(obj, 'perfil_inquili')

    @admin.display(boolean=True)
    def es_propietari(self, obj):
        return hasattr(obj, 'perfil_propietari')


@admin.register(PerfilPropietari)
class PerfilPropietariAdmin(admin.ModelAdmin):
    list_display = ['persona', 'nom_fiscal', 'nif_cif', 'iban']
    search_fields = ['persona__nom_complet', 'nom_fiscal', 'nif_cif']


class HosteInline(admin.TabularInline):
    model = Hoste
    extra = 0
    fields = ['es_principal', 'nom_complet', 'tipus_document', 'numero_document', 'email']


class ComunicacioInline(admin.TabularInline):
    model = Comunicacio
    extra = 0
    fields = ['canal', 'titol', 'destinatari', 'data', 'estat']


class ComunicacioEmailInline(admin.TabularInline):
    model = ComunicacioEmail
    extra = 0
    readonly_fields = ['tipus', 'destinatari', 'assumpte', 'enviat_a', 'enviat_per', 'exit', 'error_msg']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ReservaBasica)
class ReservaAdmin(admin.ModelAdmin):
    list_display = [
        'codi_reserva', 'immoble', 'inquili',
        'data_entrada', 'data_sortida', 'pagat', 'estat_pagament',
    ]
    list_filter = ['pagat', 'tipus_reserva', 'estat_pagament']
    search_fields = ['codi_reserva']
    inlines = [HosteInline, ComunicacioInline, ComunicacioEmailInline]


@admin.register(Hoste)
class HosteAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'reserva', 'es_principal', 'tipus_document']
    list_filter = ['es_principal', 'tipus_document']
    search_fields = ['nom_complet', 'email']


@admin.register(Comunicacio)
class ComunicacioAdmin(admin.ModelAdmin):
    list_display = ['titol', 'reserva', 'canal', 'estat', 'data', 'creat_el']
    list_filter = ['canal', 'estat']
    search_fields = ['titol', 'destinatari']


@admin.register(ComunicacioEmail)
class ComunicacioEmailAdmin(admin.ModelAdmin):
    list_display = ['tipus', 'destinatari', 'assumpte', 'reserva', 'exit', 'enviat_a']
    list_filter = ['tipus', 'exit']
    search_fields = ['destinatari', 'assumpte', 'reserva__codi_reserva']
    readonly_fields = ['reserva', 'tipus', 'destinatari', 'assumpte', 'enviat_a', 'enviat_per', 'exit', 'error_msg']
