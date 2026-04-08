from django.db import models
from properties.models import Immoble


class Inquili(models.Model):
    """Inquilí / hoste."""
    dni_passaport = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    dades_facturacio = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Inquilins'

    def __str__(self):
        return self.nom


class Reserva(models.Model):
    """Reserva d'un immoble."""
    immoble = models.ForeignKey(Immoble, on_delete=models.RESTRICT, related_name='reserves')
    inquili_principal = models.ForeignKey(Inquili, on_delete=models.RESTRICT, related_name='reserves')
    data_entrada = models.DateField()
    data_sortida = models.DateField()
    preu_total = models.DecimalField(max_digits=10, decimal_places=2)
    taxa_turistica = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estat = models.CharField(max_length=20, default='confirmada')

    class Meta:
        verbose_name_plural = 'Reserves'

    def __str__(self):
        return f"Reserva {self.id}: {self.immoble.nom_comercial}"


class ReservaHostes(models.Model):
    """Relació entre reserva i hostes."""
    reserva = models.ForeignKey(Reserva, on_delete=models.RESTRICT, related_name='hostes')
    hoste = models.ForeignKey(Inquili, on_delete=models.RESTRICT)
    es_principal = models.BooleanField(default=False)

    class Meta:
        unique_together = ('reserva', 'hoste')
        verbose_name_plural = 'Reserva Hostes'

    def __str__(self):
        return f"{self.hoste.nom} @ Reserva {self.reserva.id}"
