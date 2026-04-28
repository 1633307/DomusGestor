from django.db import models


class Immoble(models.Model):
    """
    RF-01: Gestió completa dels immobles.
    RF-02: Emmagatzemar informació tècnica dels apartaments.
    RF-04: Emmagatzemar el preu base de cada immoble.
    RF-13: Gestionar el catàleg d'immobles.
    """
    nom_comercial = models.CharField(max_length=100)
    referencia = models.CharField(max_length=50, blank=True, default='')
    adreca = models.TextField()
    ciutat = models.CharField(max_length=100, blank=True, default='')
    codi_postal = models.CharField(max_length=10, blank=True, default='')
    tipus_immoble = models.CharField(max_length=50, blank=True, default='')

    metres_quadrats = models.PositiveIntegerField(default=0)
    num_habitacions = models.PositiveIntegerField(default=0)
    num_banys = models.PositiveIntegerField(default=0)
    capacitat_maxima = models.PositiveIntegerField(default=0)
    descripcio = models.TextField(blank=True)

    preu_base_nit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    foto_principal = models.CharField(max_length=500, blank=True, default='')

    propietari_nom = models.CharField(max_length=150, blank=True, default='')
    propietari_dni = models.CharField(max_length=20, blank=True, default='')
    propietari_email = models.EmailField(blank=True, default='')
    propietari_telefon = models.CharField(max_length=30, blank=True, default='')
    propietari_adreca = models.TextField(blank=True, default='')
    propietari_iban = models.CharField(max_length=34, blank=True, default='')

    actiu = models.BooleanField(default=True)
    data_registre = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Immobles'

    def __str__(self):
        return f"{self.nom_comercial} - {self.preu_base_nit}€/nit"
