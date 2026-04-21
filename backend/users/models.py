from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuari(AbstractUser):
    nip = models.CharField(max_length=20, unique=True, verbose_name="NIP (Número d'Identificació Personal)")
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class InfoImmobiliaria(models.Model):
    """
    RF-11: Gestionar informació general de la immobiliària.
    """
    nom_comercial = models.CharField(max_length=100)
    cif = models.CharField(max_length=20, unique=True)
    adreca = models.TextField()
    email_contacte = models.EmailField()
    telefon = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Informació General Immobiliària"

    def __str__(self):
        return self.nom_comercial
