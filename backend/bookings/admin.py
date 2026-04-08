from django.contrib import admin
from .models import Inquili, Reserva, ReservaHostes


class ReservaHostesInline(admin.TabularInline):
    model = ReservaHostes
    extra = 0


@admin.register(Inquili)
class InquiliAdmin(admin.ModelAdmin):
    list_display = ['nom', 'dni_passaport', 'email']
    search_fields = ['nom', 'dni_passaport', 'email']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'immoble', 'inquili_principal', 'data_entrada', 'data_sortida', 'estat']
    list_filter = ['estat']
    search_fields = ['immoble__nom_comercial', 'inquili_principal__nom']
    inlines = [ReservaHostesInline]
