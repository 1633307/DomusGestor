from django.test import TestCase
from users.models import Usuari
from bookings.models import Persona, PerfilInquili, PerfilPropietari


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
