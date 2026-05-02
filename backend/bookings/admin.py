from django.contrib import admin

from .models import InquiliBasic, ReservaBasica, Hoste


@admin.register(InquiliBasic)
class InquiliAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'email']
    search_fields = ['nom_complet', 'email']


class HosteInline(admin.TabularInline):
    model = Hoste
    extra = 0
    fields = ['es_principal', 'nom_complet', 'tipus_document', 'numero_document', 'email']


@admin.register(ReservaBasica)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['codi_reserva', 'immoble', 'inquili', 'data_entrada', 'data_sortida', 'pagat']
    list_filter = ['pagat', 'tipus_reserva']
    search_fields = ['codi_reserva']
    inlines = [HosteInline]


@admin.register(Hoste)
class HosteAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'reserva', 'es_principal', 'tipus_document']
    list_filter = ['es_principal', 'tipus_document']
    search_fields = ['nom_complet', 'email']
