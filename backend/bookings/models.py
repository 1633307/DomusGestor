from django.db import models
from properties.models import Immoble

class InquiliBasic(models.Model):
    """
    Model per: Gestió i dades d'identitat de l'inquilí.
    """
    nom_complet = models.CharField(max_length=150)
    dni_passaport = models.CharField(max_length=20, unique=True)
    email = models.EmailField()

    def __str__(self):
        return self.nom_complet

class ReservaBasica(models.Model):
    """
    Model per: Gestió bàsica de les reserves.
    """
    immoble = models.ForeignKey(Immoble, on_delete=models.CASCADE)
    inquili = models.ForeignKey(InquiliBasic, on_delete=models.PROTECT)
    data_entrada = models.DateField()
    data_sortida = models.DateField()
    pagat = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva {self.id}: {self.immoble.nom_comercial}"