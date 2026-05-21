from django.test import TestCase
from users.models import Usuari
from bookings.models import Persona, PerfilInquili, PerfilPropietari
from properties.models import Immoble


class PersonaModelTest(TestCase):
    def test_crear_persona_basica(self):
        p = Persona.objects.create(nom_complet='Anna Garcia', email='anna@test.com')
        self.assertEqual(str(p), 'Anna Garcia')
        self.assertIsNone(p.dni_passaport_hash)

    def test_dni_hash_es_calcula_al_guardar(self):
        p = Persona.objects.create(nom_complet='Joan', dni_passaport='12345678A')
        self.assertIsNotNone(p.dni_passaport_hash)
        self.assertEqual(len(p.dni_passaport_hash), 64)

    def test_dni_hash_buit_si_no_hi_ha_dni(self):
        p = Persona.objects.create(nom_complet='Sense DNI')
        self.assertIsNone(p.dni_passaport_hash)

    def test_perfil_inquili_vincula_persona(self):
        p = Persona.objects.create(nom_complet='Llogater')
        pi = PerfilInquili.objects.create(persona=p)
        self.assertEqual(pi.persona, p)
        self.assertEqual(p.perfil_inquili, pi)

    def test_perfil_propietari_vincula_persona(self):
        p = Persona.objects.create(nom_complet='Propietari')
        pp = PerfilPropietari.objects.create(
            persona=p,
            nom_fiscal='Propietari SL',
            nif_cif='B12345678',
            iban='ES9121000418450200051332',
        )
        self.assertEqual(pp.persona, p)
        self.assertEqual(p.perfil_propietari, pp)

    def test_persona_pot_tenir_els_dos_perfils(self):
        p = Persona.objects.create(nom_complet='Dual')
        PerfilInquili.objects.create(persona=p)
        PerfilPropietari.objects.create(persona=p)
        self.assertTrue(hasattr(p, 'perfil_inquili'))
        self.assertTrue(hasattr(p, 'perfil_propietari'))


class ImmoblePropietary(TestCase):
    def test_immoble_pot_tenir_propietari_nul(self):
        immoble = Immoble.objects.create(
            nom_comercial='Pis Test',
            adreca='Carrer Major 1',
            preu_base_nit=100,
        )
        self.assertIsNone(immoble.propietari)

    def test_immoble_vincula_persona_com_a_propietari(self):
        persona = Persona.objects.create(nom_complet='Propietari Test', email='prop@test.com')
        PerfilPropietari.objects.create(persona=persona)
        immoble = Immoble.objects.create(
            nom_comercial='Pis Test 2',
            adreca='Carrer Nou 5',
            preu_base_nit=80,
            propietari=persona,
        )
        self.assertEqual(immoble.propietari, persona)
        self.assertIn(immoble, persona.immobles.all())


from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class PersonaAPITest(APITestCase):
    def setUp(self):
        self.user = Usuari.objects.create_user(
            nip='0001', username='testuser',
            email='user@test.com', password='pass1234'
        )
        self.client.force_authenticate(user=self.user)

    def test_crear_persona_via_api(self):
        url = reverse('persona-list')
        resp = self.client.post(url, {
            'nom_complet': 'Nova Persona',
            'email': 'nova@test.com',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['nom_complet'], 'Nova Persona')
        self.assertIsNone(resp.data['perfil_inquili'])
        self.assertIsNone(resp.data['perfil_propietari'])

    def test_llistar_persones(self):
        Persona.objects.create(nom_complet='Persona 1', email='p1@test.com')
        Persona.objects.create(nom_complet='Persona 2', email='p2@test.com')
        url = reverse('persona-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_detall_persona_inclou_perfils(self):
        p = Persona.objects.create(nom_complet='Amb Perfils', email='perfils@test.com')
        PerfilInquili.objects.create(persona=p)
        PerfilPropietari.objects.create(persona=p, iban='ES9121000418450200051332')
        url = reverse('persona-detail', args=[p.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data['perfil_inquili'])
        self.assertIsNotNone(resp.data['perfil_propietari'])
        self.assertEqual(resp.data['perfil_propietari']['iban'], 'ES9121000418450200051332')

    def test_dni_duplicat_retorna_error(self):
        Persona.objects.create(nom_complet='Primer', dni_passaport='12345678A')
        url = reverse('persona-list')
        resp = self.client.post(url, {
            'nom_complet': 'Segon',
            'dni_passaport': '12345678A',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dni_passaport', resp.data)

    def test_eliminar_persona(self):
        p = Persona.objects.create(nom_complet='A Eliminar', email='del@test.com')
        url = reverse('persona-detail', args=[p.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Persona.objects.filter(pk=p.pk).exists())
