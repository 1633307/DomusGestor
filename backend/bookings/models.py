from django.db import models

from core.fields import EncryptedCharField, EncryptedTextField, hmac_value
from properties.models import Immoble


class InquiliBasic(models.Model):
    """
    RF-17: Gestió de la base de dades d'inquilins.
    RF-18: Emmagatzemar dades de contacte i facturació d'inquilins.
    RF-25: Informació d'identitat de l'inquilí.
    RNF-02: dni_passaport i dades_facturacio s'emmagatzemen xifrats.
    """
    nom_complet = models.CharField(max_length=150)
    dni_passaport = EncryptedCharField()
    dni_passaport_hash = models.CharField(max_length=64, unique=True, editable=False, default='')
    email = models.EmailField()
    dades_facturacio = EncryptedTextField(blank=True)

    def save(self, *args, **kwargs):
        if self.dni_passaport:
            self.dni_passaport_hash = hmac_value(self.dni_passaport)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Inquilí'
        verbose_name_plural = 'Inquilins'

    def __str__(self):
        return self.nom_complet


class ReservaBasica(models.Model):
    """
    RF-23: Gestió bàsica de les reserves.
    """
    immoble = models.ForeignKey(Immoble, on_delete=models.CASCADE, related_name='reserves')
    inquili = models.ForeignKey(InquiliBasic, on_delete=models.PROTECT, related_name='reserves')
    data_entrada = models.DateField()
    data_sortida = models.DateField()
    pagat = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reserves'

    def __str__(self):
        return f"Reserva {self.id}: {self.immoble.nom_comercial}"
