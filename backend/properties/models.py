from django.db import models
from users.models import InfoImmobiliaria

class Immoble(models.Model):
    """
    Model per:
    - Gestió i catàleg d'immobles.
    - Emmagatzemar informació tècnica.
    - Emmagatzemar el preu base.
    """
    nom_comercial = models.CharField(max_length=100)
    adreca = models.TextField()
    
    # Informació tècnica
    metres_quadrats = models.PositiveIntegerField()
    num_habitacions = models.PositiveIntegerField()
    num_banys = models.PositiveIntegerField()
    capacitat_maxima = models.PositiveIntegerField()
    descripcio = models.TextField(blank=True)
    
    # Preu base
    preu_base_nit = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Camps auxiliars per al catàleg
    actiu = models.BooleanField(default=True)
    data_registre = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_comercial} - {self.preu_base_nit}€/nit"