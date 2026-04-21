from django.contrib import admin

from .models import InquiliBasic, ReservaBasica


@admin.register(InquiliBasic)
class InquiliAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'email']
    search_fields = ['nom_complet', 'email']


@admin.register(ReservaBasica)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'immoble', 'inquili', 'data_entrada', 'data_sortida', 'pagat']
    list_filter = ['pagat']
