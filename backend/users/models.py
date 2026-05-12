from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UsuariManager(BaseUserManager):
    def create_user(self, nip, username, email, password, **extra_fields):
        if not nip:
            raise ValueError('El NIP és obligatori')
        email = self.normalize_email(email)
        user = self.model(nip=nip, username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Usuari(AbstractBaseUser):
    username    = models.CharField(max_length=150, unique=True)
    first_name  = models.CharField(max_length=150, blank=True)
    last_name   = models.CharField(max_length=150, blank=True)
    email       = models.EmailField(unique=True)
    nip         = models.CharField(
        max_length=20, unique=True,
        verbose_name="NIP (Número d'Identificació Personal)"
    )
    is_active   = models.BooleanField(default=True)
    is_admin    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD  = 'nip'
    REQUIRED_FIELDS = ['username', 'email']

    objects = UsuariManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin


class InfoImmobiliaria(models.Model):
    nom_comercial   = models.CharField(max_length=100)
    cif             = models.CharField(max_length=20, unique=True)
    adreca          = models.TextField()
    email_contacte  = models.EmailField()
    telefon         = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Informació General Immobiliària"

    def __str__(self):
        return self.nom_comercial
