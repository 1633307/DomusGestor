from django.test import TestCase, override_settings
from django.core import mail
from rest_framework.test import APIClient

from bookings.models import ComunicacioEmail, Comunicacio, ReservaBasica, Persona
from properties.models import Immoble
from users.models import Usuari, InfoImmobiliaria


def _setup():
    InfoImmobiliaria.objects.create(
        nom_comercial='Gestor', cif='B00000001',
        adreca='C/1', email_contacte='g@test.com', telefon='600000000',
    )
    user = Usuari.objects.create_user(nip='001', username='admin', email='a@test.com', password='pass')
    inquili = Persona.objects.create(nom_complet='Inquilí', email='inq@test.com')
    immoble = Immoble.objects.create(nom_comercial='Pis', adreca='C/1')
    reserva = ReservaBasica.objects.create(
        immoble=immoble, inquili=inquili,
        data_entrada='2026-07-01', data_sortida='2026-07-07',
        estat_reserva='reservada', tipus_reserva='Direct',
        codi_reserva='RES-2026-TEST',
    )
    return user, reserva


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ManualEmailSendTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user, self.reserva = _setup()
        self.client.force_authenticate(user=self.user)

    def test_crear_comunicacio_email_envia_correu(self):
        resp = self.client.post(
            f'/api/bookings/reserves/{self.reserva.pk}/comunicacions/',
            {'canal': 'Email', 'titol': 'Benvinguda', 'destinatari': 'inq@test.com',
             'estat': 'pendent', 'resum': 'Benvingut!'},
            format='json',
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['inq@test.com'])

    def test_crear_comunicacio_email_marca_com_enviada(self):
        self.client.post(
            f'/api/bookings/reserves/{self.reserva.pk}/comunicacions/',
            {'canal': 'Email', 'titol': 'Test', 'destinatari': 'inq@test.com',
             'estat': 'pendent', 'resum': 'Contingut'},
            format='json',
        )
        self.assertEqual(Comunicacio.objects.first().estat, 'enviada')

    def test_canal_no_email_no_envia(self):
        self.client.post(
            f'/api/bookings/reserves/{self.reserva.pk}/comunicacions/',
            {'canal': 'Telefon', 'titol': 'Trucada', 'destinatari': '600000000',
             'estat': 'enviada', 'resum': 'Fet'},
            format='json',
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_llista_emails_endpoint(self):
        ComunicacioEmail.objects.create(
            reserva=self.reserva, tipus='manual',
            destinatari='a@b.com', assumpte='Test', exit=True,
        )
        resp = self.client.get(f'/api/bookings/reserves/{self.reserva.pk}/emails/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['tipus'], 'manual')
