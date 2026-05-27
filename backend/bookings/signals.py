import logging

from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .emails import enviar_prereservada, enviar_confirmada, enviar_cancelada, enviar_pagament
from .models import ReservaBasica, PagamentReserva

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=ReservaBasica)
def reserva_captura_estat_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._estat_anterior = sender.objects.get(pk=instance.pk).estat_reserva
        except sender.DoesNotExist:
            instance._estat_anterior = None
    else:
        instance._estat_anterior = None


@receiver(post_save, sender=ReservaBasica)
def reserva_post_save(sender, instance, created, **kwargs):
    estat_anterior = getattr(instance, '_estat_anterior', None)
    reserva_pk = instance.pk

    def _send():
        try:
            reserva = ReservaBasica.objects.select_related(
                'immoble', 'immoble__propietari', 'inquili'
            ).prefetch_related('hostes').get(pk=reserva_pk)
        except ReservaBasica.DoesNotExist:
            return

        if created:
            if reserva.estat_reserva == 'prereservada':
                logger.info('Reserva nova prereservada: id=%s', reserva.pk)
                enviar_prereservada(reserva)
            return

        if estat_anterior == reserva.estat_reserva:
            return

        logger.info('Canvi estat reserva: id=%s %s -> %s', reserva.pk, estat_anterior, reserva.estat_reserva)
        if reserva.estat_reserva == 'reservada':
            enviar_confirmada(reserva)
        elif reserva.estat_reserva == 'cancelada':
            enviar_cancelada(reserva)

    transaction.on_commit(_send)


@receiver(pre_save, sender=PagamentReserva)
def pagament_captura_estat_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._estat_anterior = sender.objects.get(pk=instance.pk).estat
        except sender.DoesNotExist:
            instance._estat_anterior = None
    else:
        instance._estat_anterior = None


@receiver(post_save, sender=PagamentReserva)
def pagament_post_save(sender, instance, created, **kwargs):
    estat_anterior = getattr(instance, '_estat_anterior', None)
    pagament_pk = instance.pk

    def _send():
        try:
            pagament = PagamentReserva.objects.select_related(
                'reserva__immoble__propietari', 'reserva__inquili'
            ).get(pk=pagament_pk)
        except PagamentReserva.DoesNotExist:
            return
        if pagament.estat == 'pagat' and estat_anterior != 'pagat':
            logger.info('Pagament confirmat: pagament_id=%s reserva_id=%s', pagament.pk, pagament.reserva_id)
            enviar_pagament(pagament.reserva, pagament)

    transaction.on_commit(_send)
