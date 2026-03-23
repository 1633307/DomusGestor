from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuari(AbstractUser):
    """
    Model d'usuari accés per a la immobiliària.
    Compleix amb:
    """
    nip = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name="NIP (Número d'Identificació Personal)"
    )
    
    # L'email és necessari per a la info de contacte bàsica
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class InfoImmobiliaria(models.Model):
    """
    Model per: Gestionar informació general de la immobiliària.
    """
    nom_comercial = models.CharField(max_length=100)
    cif = models.CharField(max_length=20, unique=True)
    adreca = models.TextField()
    email_contacte = models.EmailField()
    telefon = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Informació General Immobiliària"