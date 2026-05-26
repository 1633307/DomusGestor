from django.test import TestCase
from bookings.models import ComunicacioEmail, ReservaBasica, Persona
from properties.models import Immoble


def _make_reserva():
    persona = Persona.objects.create(nom_complet='Test', email='test@test.com')
    immoble = Immoble.objects.create(nom_comercial='Pis', adreca='Carrer 1')
    return ReservaBasica.objects.create(
        immoble=immoble, inquili=persona,
        data_entrada='2026-07-01', data_sortida='2026-07-07',
    )


class ComunicacioEmailModelTest(TestCase):
    def test_crear_log_exit(self):
        reserva = _make_reserva()
        log = ComunicacioEmail.objects.create(
            reserva=reserva, tipus='prereservada_inquili',
            destinatari='test@test.com', assumpte='Test', exit=True,
        )
        self.assertTrue(log.exit)
        self.assertIsNone(log.enviat_per)
        self.assertEqual(log.error_msg, '')

    def test_crear_log_error(self):
        reserva = _make_reserva()
        log = ComunicacioEmail.objects.create(
            reserva=reserva, tipus='prereservada_inquili',
            destinatari='', assumpte='Test', exit=False, error_msg='Sense email',
        )
        self.assertFalse(log.exit)
        self.assertEqual(log.error_msg, 'Sense email')

    def test_str(self):
        reserva = _make_reserva()
        log = ComunicacioEmail.objects.create(
            reserva=reserva, tipus='confirmada_inquili',
            destinatari='a@b.com', assumpte='Confirmada', exit=True,
        )
        self.assertIn('confirmada_inquili', str(log))
