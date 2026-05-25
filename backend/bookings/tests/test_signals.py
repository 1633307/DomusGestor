from django.test import TransactionTestCase, override_settings
from django.core import mail

from bookings.models import ComunicacioEmail, ReservaBasica, Persona, PagamentReserva
from properties.models import Immoble
from users.models import InfoImmobiliaria


def _setup():
    InfoImmobiliaria.objects.create(
        nom_comercial='Gestor', cif='B00000001',
        adreca='C/1', email_contacte='g@test.com', telefon='600000000',
    )
    propietari = Persona.objects.create(nom_complet='Propietari', email='prop@test.com')
    inquili = Persona.objects.create(nom_complet='Inquilí', email='inq@test.com')
    immoble = Immoble.objects.create(nom_comercial='Pis', adreca='C/1', propietari=propietari)
    return inquili, immoble


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReservaSignalsTest(TransactionTestCase):
    def test_prereservada_envia_emails_en_crear(self):
        inquili, immoble = _setup()
        ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='prereservada', tipus_reserva='Direct',
        )
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(ComunicacioEmail.objects.count(), 2)

    def test_no_envia_si_estat_inicial_none(self):
        inquili, immoble = _setup()
        ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva=None,
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_canvi_a_reservada_envia_emails(self):
        inquili, immoble = _setup()
        reserva = ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='prereservada', tipus_reserva='Direct',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        reserva.estat_reserva = 'reservada'
        reserva.save()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(ComunicacioEmail.objects.filter(tipus__contains='confirmada').count(), 2)

    def test_canvi_a_cancelada_envia_emails(self):
        inquili, immoble = _setup()
        reserva = ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='reservada', tipus_reserva='Direct',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        reserva.estat_reserva = 'cancelada'
        reserva.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_save_sense_canvi_estat_no_envia(self):
        inquili, immoble = _setup()
        reserva = ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='reservada', tipus_reserva='Direct',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        reserva.comentaris_interns = 'Canvi sense importància'
        reserva.save()
        self.assertEqual(len(mail.outbox), 0)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PagamentSignalsTest(TransactionTestCase):
    def _make_reserva(self):
        _setup()
        inquili = Persona.objects.get(nom_complet='Inquilí')
        immoble = Immoble.objects.get(nom_comercial='Pis')
        return ReservaBasica.objects.create(
            immoble=immoble, inquili=inquili,
            data_entrada='2026-07-01', data_sortida='2026-07-07',
            estat_reserva='reservada', tipus_reserva='Direct',
            import_total='500.00', import_pendent='250.00',
        )

    def test_pagament_creat_com_pagat_envia_emails(self):
        reserva = self._make_reserva()
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pagat',
        )
        self.assertEqual(len(mail.outbox), 2)

    def test_pagament_pendent_no_envia(self):
        reserva = self._make_reserva()
        mail.outbox.clear()
        PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pendent',
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_canvi_pendent_a_pagat_envia_emails(self):
        reserva = self._make_reserva()
        pagament = PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pendent',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        pagament.estat = 'pagat'
        pagament.save()
        self.assertEqual(len(mail.outbox), 2)

    def test_save_pagament_pagat_sense_canvi_no_reenvia(self):
        reserva = self._make_reserva()
        pagament = PagamentReserva.objects.create(
            reserva=reserva, data_pagament='2026-06-01',
            import_pagament='250.00', metode_pagament='transferencia', estat='pagat',
        )
        mail.outbox.clear()
        ComunicacioEmail.objects.all().delete()
        pagament.import_pagament = '251.00'
        pagament.save()
        self.assertEqual(len(mail.outbox), 0)
