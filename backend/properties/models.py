from django.contrib.postgres.fields import ArrayField
from django.db import models


class Servei(models.Model):
    CATEGORIES = [
        ('climatitzacio',    'Climatització'),
        ('conectivitat',     'Connectivitat'),
        ('electrodomestics', 'Electrodomèstics'),
        ('exterior',         'Exterior'),
        ('altres',           'Altres'),
    ]

    nom       = models.CharField(max_length=100, unique=True)
    icona     = models.CharField(max_length=50, blank=True, default='')
    categoria = models.CharField(max_length=20, choices=CATEGORIES, default='altres')

    class Meta:
        verbose_name_plural = 'Serveis'
        ordering = ['categoria', 'nom']

    def __str__(self):
        return self.nom


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
    descompte_actiu = models.BooleanField(default=False)
    descompte_percentatge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fotos = ArrayField(models.CharField(max_length=500), blank=True, default=list)

    propietari = models.ForeignKey(
        'bookings.Persona',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='immobles',
    )

    hora_checkin_inici  = models.TimeField(null=True, blank=True)
    hora_checkin_fi     = models.TimeField(null=True, blank=True)
    hora_checkout_inici = models.TimeField(null=True, blank=True)
    hora_checkout_fi    = models.TimeField(null=True, blank=True)

    serveis = models.ManyToManyField(Servei, blank=True, related_name='immobles')

    actiu = models.BooleanField(default=True)
    data_registre = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Immobles'

    def __str__(self):
        return f"{self.nom_comercial} - {self.preu_base_nit}€/nit"


class Temporada(models.Model):
    comissio = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    immoble      = models.ForeignKey(Immoble, on_delete=models.CASCADE, related_name='temporades')
    nom          = models.CharField(max_length=100)
    data_inici   = models.DateField()
    data_fi      = models.DateField()
    preu_nit     = models.DecimalField(max_digits=10, decimal_places=2)
    min_nits     = models.PositiveIntegerField(default=1)
    dies_checkin = ArrayField(models.IntegerField(), blank=True, default=list)

    class Meta:
        verbose_name_plural = 'Temporades'
        ordering = ['data_inici']

    def __str__(self):
        return f"{self.nom} ({self.immoble.nom_comercial}): {self.data_inici} → {self.data_fi}"
