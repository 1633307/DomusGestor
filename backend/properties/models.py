from django.db import models
from users.models import Propietari


class Immoble(models.Model):
    """Immoble turístic."""

    class EstatNeteja(models.TextChoices):
        NET = 'net', 'Net'
        PENDENT = 'pendent', 'Pendent'

    propietari = models.ForeignKey(
        Propietari,
        on_delete=models.RESTRICT,
        related_name='immobles',
        null=True,
        blank=True,
    )
    nom_comercial = models.CharField(max_length=100)
    adreca = models.TextField()
    preu_base = models.DecimalField(max_digits=10, decimal_places=2)
    estat_neteja = models.CharField(
        max_length=10,
        choices=EstatNeteja.choices,
        default=EstatNeteja.NET,
    )
    info_tecnica = models.JSONField(default=dict, blank=True)

    # Camps extres del model original
    metres_quadrats = models.PositiveIntegerField(default=0)
    num_habitacions = models.PositiveIntegerField(default=0)
    num_banys = models.PositiveIntegerField(default=0)
    capacitat_maxima = models.PositiveIntegerField(default=1)
    descripcio = models.TextField(blank=True)
    actiu = models.BooleanField(default=True)
    data_registre = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_comercial} - {self.preu_base}€/nit"


class Temporada(models.Model):
    """Temporada de preus per a un immoble."""
    immoble = models.ForeignKey(Immoble, on_delete=models.RESTRICT, related_name='temporades')
    nom_descriptiu = models.CharField(max_length=50)
    data_inici = models.DateField()
    data_fi = models.DateField()
    preu_nit = models.DecimalField(max_digits=10, decimal_places=2)
    min_nits = models.PositiveIntegerField(default=1)
    dia_checkin_permis = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Temporades'

    def __str__(self):
        return f"{self.nom_descriptiu} ({self.immoble.nom_comercial})"
