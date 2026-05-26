from django.test import TestCase, override_settings
from django.core import mail
from unittest.mock import patch

from bookings.emails import enviar_prereservada, enviar_confirmada, enviar_cancelada, enviar_pagament
from bookings.models import ComunicacioEmail, ReservaBasica, Persona, PagamentReserva
from properties.models import Immoble
from users.models import InfoImmobiliaria


def _setup():
    InfoImmobiliaria.objects.create(
        nom_comercial='Gestor Test', cif='B12345678',
        adreca='Carrer 1', email_contacte='gestor@test.com', telefon='600000000',
    )
    propietari = Persona.objects.create(nom_complet='Propietari', email='propietari@test.com')
    inquili = Persona.objects.create(nom_complet='Inquilí', email='inquili@test.com')
    immoble = Immoble.objects.create(nom_comercial='Pis', adreca='Carrer 1', propietari=propietari)
    reserva = ReservaBasica.objects.create(
        immoble=immoble, inquili=inquili,
        data_entrada='2026-07-01', data_sortida='2026-07-07',
        codi_reserva='RES-2026-0001', estat_reserva='prereservada',
        tipus_reserva='Direct', num_hostes=2,
        import_total='500.00', import_pendent='500.00',
    )
    return reserva


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnviarPrereservadaTest(TestCase):
    def test_envia_dos_emails_directa(self):
        reserva = _setup()
        enviar_prereservada(reserva)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(ComunicacioEmail.objects.filter(exit=True).count(), 2)

    def test_envia_solo_propietari_si_airbnb(self):
        reserva = _setup()
        reserva.tipus_reserva = 'Airbnb'
        enviar_prereservada(reserva)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['propietari@test.com'])

    def test_log_error_si_sense_email(self):
        reserva = _setup()
        reserva.inquili.email = ''
        reserva.inquili.save(update_fields=['email'])
        enviar_prereservada(reserva)
        log = ComunicacioEmail.objects.get(tipus='prereservada_inquili')
        self.assertFalse(log.exit)
        self.assertEqual(log.error_msg, 'Sense email')

    def test_log_error_si_smtp_falla(self):
        reserva = _setup()
        with patch('bookings.emails.send_mail', side_effect=Exception('SMTP error')):
            enviar_prereservada(reserva)
        self.assertTrue(ComunicacioEmail.objects.filter(exit=False).exists())
        self.assertIn('SMTP error', ComunicacioEmail.objects.filter(exit=False).first().error_msg)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnviarConfirmadaTest(TestCase):
    def test_envia_dos_emails(self):
        enviar_confirmada(_setup())
        self.assertEqual(len(mail.outbox), 2)

    def test_assumpte_conte_codi_reserva(self):
        reserva = _setup()
        enviar_confirmada(reserva)
        self.assertTrue(any('RES-2026-0001' in m.subject for m in mail.outbox))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnviarCanceladaTest(TestCase):
    def test_envia_dos_emails(self):
        enviar_cancelada(_setup())
        self.assertEqual(len(mail.outbox), 2)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnviarPagamentTest(TestCase):
    def test_envia_dos_emails(self):
        reserva = _setup()
        pagament = PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pagat',
        )
        enviar_pagament(reserva, pagament)
        self.assertEqual(len(mail.outbox), 2)
