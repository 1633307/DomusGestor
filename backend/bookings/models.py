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
    TIPUS_CHOICES = [
        ('Airbnb', 'Airbnb'),
        ('Booking', 'Booking'),
        ('Direct', 'Directa'),
        ('Altres', 'Altres'),
    ]

    immoble = models.ForeignKey(Immoble, on_delete=models.CASCADE, related_name='reserves')
    inquili = models.ForeignKey(InquiliBasic, on_delete=models.PROTECT, related_name='reserves')
    data_entrada = models.DateField()
    data_sortida = models.DateField()
    pagat = models.BooleanField(default=False)

    codi_reserva = models.CharField(max_length=30, blank=True, default='')
    tipus_reserva = models.CharField(max_length=20, choices=TIPUS_CHOICES, blank=True, default='')
    comentaris_interns = models.TextField(blank=True, default='')
    num_hostes = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reserves'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-generate codi_reserva si està buit
        if not self.codi_reserva:
            entrada = self.data_entrada
            year = entrada.year if hasattr(entrada, 'year') else str(entrada)[:4]
            self.codi_reserva = f"RES-{year}-{self.id:04d}"
            ReservaBasica.objects.filter(pk=self.pk).update(codi_reserva=self.codi_reserva)

    def __str__(self):
        return f"Reserva {self.codi_reserva or self.id}: {self.immoble.nom_comercial}"


class Hoste(models.Model):
    """
    RF-25: Informació d'identitat dels hostes que ocupen una reserva.
    RNF-02: numero_document s'emmagatzema xifrat.
    """
    GENERE_CHOICES = [
        ('Home', 'Home'),
        ('Dona', 'Dona'),
        ('Altres', 'Altres'),
    ]
    DOCUMENT_CHOICES = [
        ('DNI', 'DNI'),
        ('NIE', 'NIE'),
        ('Passaport', 'Passaport'),
    ]

    reserva = models.ForeignKey(
        ReservaBasica, on_delete=models.CASCADE, related_name='hostes'
    )
    es_principal = models.BooleanField(default=False)

    nom_complet = models.CharField(max_length=150)
    genere = models.CharField(max_length=10, choices=GENERE_CHOICES, blank=True, default='')
    relacio_parental = models.CharField(max_length=30, blank=True, default='')
    tipus_document = models.CharField(max_length=15, choices=DOCUMENT_CHOICES, blank=True, default='')
    numero_document = EncryptedCharField(blank=True, default='')
    numero_document_hash = models.CharField(max_length=64, blank=True, default='', editable=False)
    nacionalitat = models.CharField(max_length=80, blank=True, default='')
    data_naixement = models.DateField(null=True, blank=True)
    residencia = models.TextField(blank=True, default='')
    email = models.EmailField(blank=True, default='')
    telefon = models.CharField(max_length=30, blank=True, default='')

    class Meta:
        verbose_name = 'Hoste'
        verbose_name_plural = 'Hostes'
        ordering = ['-es_principal', 'id']

    def save(self, *args, **kwargs):
        if self.numero_document:
            self.numero_document_hash = hmac_value(self.numero_document)
        else:
            self.numero_document_hash = ''
        super().save(*args, **kwargs)

    def __str__(self):
        prefix = 'Principal' if self.es_principal else 'Hoste'
        return f"{prefix}: {self.nom_complet}"
