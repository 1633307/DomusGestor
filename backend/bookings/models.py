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

    nom_complet = models.CharField(max_length=150)
    dni_passaport = EncryptedCharField(blank=True, default='')
    dni_passaport_hash = models.CharField(
        max_length=64, unique=True, null=True, blank=True, editable=False, default=None
    )
    email = models.EmailField(blank=True, default='')
    dades_facturacio = EncryptedTextField(blank=True)
    genere = models.CharField(max_length=10, choices=GENERE_CHOICES, blank=True, default='')
    tipus_document = models.CharField(max_length=15, choices=DOCUMENT_CHOICES, blank=True, default='')
    nacionalitat = models.CharField(max_length=80, blank=True, default='')
    data_naixement = models.DateField(null=True, blank=True)
    residencia = models.TextField(blank=True, default='')
    telefon = models.CharField(max_length=30, blank=True, default='')
    nom_fiscal = models.CharField(max_length=150, blank=True, default='')
    nif_cif = models.CharField(max_length=30, blank=True, default='')
    adreca_facturacio = models.TextField(blank=True, default='')
    codi_postal_facturacio = models.CharField(max_length=12, blank=True, default='')
    ciutat_facturacio = models.CharField(max_length=100, blank=True, default='')
    provincia_facturacio = models.CharField(max_length=100, blank=True, default='')
    pais_facturacio = models.CharField(max_length=100, blank=True, default='')
    email_facturacio = models.EmailField(blank=True, default='')
    telefon_facturacio = models.CharField(max_length=30, blank=True, default='')
    observacions_facturacio = models.TextField(blank=True, default='')

    def save(self, *args, **kwargs):
        if self.dni_passaport:
            self.dni_passaport_hash = hmac_value(self.dni_passaport)
        else:
            self.dni_passaport_hash = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Inquilí'
        verbose_name_plural = 'Inquilins'
        ordering = ['nom_complet']

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
    ESTAT_RESERVA_CHOICES = [
        ('prereservada', 'Prereservada'),
        ('reservada', 'Reservada'),
        ('lista', 'Lista'),
        ('cancelada', 'Cancelada'),
    ]

    immoble = models.ForeignKey(Immoble, on_delete=models.CASCADE, related_name='reserves')
    inquili = models.ForeignKey(InquiliBasic, on_delete=models.PROTECT, related_name='reserves')
    data_entrada = models.DateField()
    data_sortida = models.DateField()
    pagat = models.BooleanField(default=False)

    codi_reserva = models.CharField(max_length=30, blank=True, default='')
    tipus_reserva = models.CharField(max_length=20, choices=TIPUS_CHOICES, blank=True, default='')
    estat_reserva = models.CharField(
        max_length=20,
        choices=ESTAT_RESERVA_CHOICES,
        blank=True,
        null=True,
        default=None,
    )
    net = models.BooleanField(default=False)
    comentaris_interns = models.TextField(blank=True, default='')
    num_hostes = models.PositiveIntegerField(default=0)
    descompte_immoble_aplicat = models.BooleanField(default=False)
    descompte_immoble_percentatge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descompte_individual_aplicat = models.BooleanField(default=False)
    descompte_individual_percentatge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    descompte_individual_motiu = models.TextField(blank=True, default='')

    ESTAT_PAGAMENT_CHOICES = [
        ('pendent', 'Pendent'),
        ('parcial', 'Parcial'),
        ('pagada', 'Pagada'),
        ('retornada', 'Retornada'),
        ('rebutjada', 'Rebutjada'),
    ]

    estat_pagament = models.CharField(
        max_length=20, choices=ESTAT_PAGAMENT_CHOICES, default='pendent'
    )
    import_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    import_pagat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    import_pendent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fianca = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    metode_pagament = models.CharField(max_length=50, blank=True, default='')
    data_ultim_pagament = models.DateField(null=True, blank=True)
    observacions_pagament = models.TextField(blank=True, default='')

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


class PagamentReserva(models.Model):
    METODE_CHOICES = [
        ('efectiu',       'Efectiu'),
        ('transferencia', 'Transferència'),
        ('targeta',       'Targeta'),
        ('bizum',         'Bizum'),
        ('altres',        'Altres'),
    ]
    ESTAT_CHOICES = [
        ('pendent',  'Pendent'),
        ('pagat',    'Pagat'),
        ('cancelat', 'Cancel·lat'),
    ]

    reserva          = models.ForeignKey(ReservaBasica, on_delete=models.CASCADE, related_name='pagaments')
    data_pagament    = models.DateField()
    import_pagament  = models.DecimalField(max_digits=10, decimal_places=2)
    metode_pagament  = models.CharField(max_length=20, choices=METODE_CHOICES, default='transferencia')
    estat            = models.CharField(max_length=20, choices=ESTAT_CHOICES, default='pendent')

    class Meta:
        verbose_name = 'Pagament'
        verbose_name_plural = 'Pagaments'
        ordering = ['-data_pagament']

    def __str__(self):
        return f"{self.import_pagament}€ · {self.reserva.codi_reserva} ({self.estat})"


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


class Comunicacio(models.Model):
    CANAL_CHOICES = [
        ('Email', 'Email'),
        ('Telefon', 'Telèfon'),
        ('WhatsApp', 'WhatsApp'),
        ('Sistema', 'Sistema'),
    ]
    ESTAT_CHOICES = [
        ('enviada', 'Enviada'),
        ('pendent', 'Pendent'),
        ('error', 'Error'),
        ('programada', 'Programada'),
    ]

    reserva = models.ForeignKey(
        ReservaBasica, on_delete=models.CASCADE, related_name='comunicacions'
    )
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES)
    titol = models.CharField(max_length=200)
    destinatari = models.CharField(max_length=200, blank=True, default='')
    data = models.DateField(null=True, blank=True)
    estat = models.CharField(max_length=20, choices=ESTAT_CHOICES, default='pendent')
    resum = models.TextField(blank=True, default='')
    creat_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Comunicació'
        verbose_name_plural = 'Comunicacions'
        ordering = ['-creat_el']

    def __str__(self):
        return f"{self.canal}: {self.titol}"
