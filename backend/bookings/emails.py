import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from users.models import InfoImmobiliaria
from .models import ComunicacioEmail

logger = logging.getLogger(__name__)


def _get_remitent():
    return InfoImmobiliaria.objects.first()


def _envia_i_registra(reserva, tipus, destinatari_email, assumpte, template, context, enviat_per=None):
    if not destinatari_email:
        logger.warning('Email sense destinatari: tipus=%s reserva_id=%s', tipus, reserva.pk)
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus=tipus, destinatari='', assumpte=assumpte,
            enviat_per=enviat_per, exit=False, error_msg='Sense email',
        )
        return
    try:
        html = render_to_string(template, context)
        from_email = context['immobiliaria'].email_contacte if context.get('immobiliaria') else None
        send_mail(
            subject=assumpte, message=strip_tags(html), from_email=from_email,
            recipient_list=[destinatari_email], html_message=html, fail_silently=False,
        )
        logger.info('Email enviat: tipus=%s reserva_id=%s destinatari=%s', tipus, reserva.pk, destinatari_email)
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus=tipus, destinatari=destinatari_email,
            assumpte=assumpte, enviat_per=enviat_per, exit=True,
        )
    except Exception as exc:
        logger.error('Error enviant email: tipus=%s reserva_id=%s error=%s', tipus, reserva.pk, exc)
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus=tipus, destinatari=destinatari_email,
            assumpte=assumpte, enviat_per=enviat_per, exit=False, error_msg=str(exc),
        )


def _es_plataforma_externa(reserva):
    return reserva.tipus_reserva in ('Airbnb', 'Booking')


def _propietari_email(reserva):
    return reserva.immoble.propietari.email if reserva.immoble.propietari else ''


def enviar_prereservada(reserva):
    immobiliaria = _get_remitent()
    ctx = {'reserva': reserva, 'immobiliaria': immobiliaria}
    if not _es_plataforma_externa(reserva):
        _envia_i_registra(reserva, 'prereservada_inquili', reserva.inquili.email,
                          f'Sol·licitud de reserva rebuda – {reserva.codi_reserva}',
                          'emails/prereservada_inquili.html', ctx)
    _envia_i_registra(reserva, 'prereservada_propietari', _propietari_email(reserva),
                      f'Nova sol·licitud de reserva – {reserva.immoble.nom_comercial}',
                      'emails/prereservada_propietari.html', ctx)


def enviar_confirmada(reserva):
    immobiliaria = _get_remitent()
    ctx = {'reserva': reserva, 'immobiliaria': immobiliaria}
    if not _es_plataforma_externa(reserva):
        _envia_i_registra(reserva, 'confirmada_inquili', reserva.inquili.email,
                          f'La teva reserva est\xe0 confirmada! – {reserva.codi_reserva}',
                          'emails/confirmada_inquili.html', ctx)
    _envia_i_registra(reserva, 'confirmada_propietari', _propietari_email(reserva),
                      f'Reserva confirmada – {reserva.immoble.nom_comercial}',
                      'emails/confirmada_propietari.html', ctx)


def enviar_cancelada(reserva):
    immobiliaria = _get_remitent()
    ctx = {'reserva': reserva, 'immobiliaria': immobiliaria}
    if not _es_plataforma_externa(reserva):
        _envia_i_registra(reserva, 'cancelada_inquili', reserva.inquili.email,
                          f'Reserva cancel\xb7lada – {reserva.codi_reserva}',
                          'emails/cancelada_inquili.html', ctx)
    _envia_i_registra(reserva, 'cancelada_propietari', _propietari_email(reserva),
                      f'Reserva cancel\xb7lada – {reserva.immoble.nom_comercial}',
                      'emails/cancelada_propietari.html', ctx)


def enviar_pagament(reserva, pagament):
    immobiliaria = _get_remitent()
    ctx = {'reserva': reserva, 'immobiliaria': immobiliaria, 'pagament': pagament}
    _envia_i_registra(reserva, 'pagament_inquili', reserva.inquili.email,
                      f'Pagament confirmat – {reserva.codi_reserva}',
                      'emails/pagament_inquili.html', ctx)
    _envia_i_registra(reserva, 'pagament_propietari', _propietari_email(reserva),
                      f'Pagament rebut – {reserva.immoble.nom_comercial}',
                      'emails/pagament_propietari.html', ctx)


def enviar_comunicacio_manual(reserva, comunicacio, usuari=None):
    immobiliaria = _get_remitent()
    from_email = immobiliaria.email_contacte if immobiliaria else None
    destinatari = comunicacio.destinatari

    if not destinatari:
        logger.warning('Comunicació manual sense destinatari: comunicacio_id=%s reserva_id=%s', comunicacio.pk, reserva.pk)
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus='manual', destinatari='',
            assumpte=comunicacio.titol, enviat_per=usuari, exit=False, error_msg='Sense email',
        )
        comunicacio.estat = 'error'
        comunicacio.save(update_fields=['estat'])
        return

    try:
        send_mail(
            subject=comunicacio.titol,
            message=comunicacio.resum or '',
            from_email=from_email,
            recipient_list=[destinatari],
            html_message=f'<p>{comunicacio.resum}</p>' if comunicacio.resum else None,
            fail_silently=False,
        )
        logger.info('Comunicació manual enviada: comunicacio_id=%s reserva_id=%s destinatari=%s', comunicacio.pk, reserva.pk, destinatari)
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus='manual', destinatari=destinatari,
            assumpte=comunicacio.titol, enviat_per=usuari, exit=True,
        )
        comunicacio.estat = 'enviada'
        comunicacio.save(update_fields=['estat'])
    except Exception as exc:
        logger.error('Error comunicació manual: comunicacio_id=%s reserva_id=%s error=%s', comunicacio.pk, reserva.pk, exc)
        ComunicacioEmail.objects.create(
            reserva=reserva, tipus='manual', destinatari=destinatari,
            assumpte=comunicacio.titol, enviat_per=usuari, exit=False, error_msg=str(exc),
        )
        comunicacio.estat = 'error'
        comunicacio.save(update_fields=['estat'])
