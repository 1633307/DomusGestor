from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuari(AbstractUser):
    """Model d'usuari d'accés per a la immobiliària."""

    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        GESTOR = 'gestor', 'Gestor'

    nip = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="NIP (Número d'Identificació Personal)",
    )
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=10, choices=Rol.choices, default=Rol.GESTOR)

    def __str__(self):
        return f"{self.username} ({self.rol})"


class Propietari(models.Model):
    """Propietari d'immobles."""
    dni_nie = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    dades_fiscals = models.TextField(blank=True)
    email = models.EmailField()

    class Meta:
        verbose_name_plural = 'Propietaris'

    def __str__(self):
        return self.nom


class InfoImmobiliaria(models.Model):
    """Informació general de la immobiliària."""
    nom_comercial = models.CharField(max_length=100)
    cif = models.CharField(max_length=20, unique=True)
    adreca = models.TextField()
    email_contacte = models.EmailField()
    telefon = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Informació General Immobiliària"

    def __str__(self):
        return self.nom_comercial
