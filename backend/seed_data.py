"""
Seed script: crea un usuari admin, 20 immobles, 50 inquilins i ~210 reserves.
Executa'l des de la carpeta backend/:

python seed_data.py

AVIS: esborra tots els registres existents de reserves, inquilins i immobles
abans de crear-ne de nous. L'usuari admin NO s'esborra si ja existeix.

REQUISIT PREVI, EXECUTAR A LA CARPETA DE BACKEND: python manage.py migrate

Credencials de l'usuari creat:
    NIP:      ADM001
    Password: DomusGestor2026!
"""

import os
import sys
from datetime import date, timedelta

import django

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domusgestor.settings")
django.setup()

from users.models import Usuari
from properties.models import Immoble, Servei, Temporada
from bookings.models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Hoste, PagamentReserva


def run():
    # ── Usuari admin ─────────────────────────────────────────────────────────
    if Usuari.objects.filter(nip="ADM001").exists() or Usuari.objects.filter(username="admin").exists():
        print("Usuari admin ja existeix, no s'ha sobreescrit")
    else:
        Usuari.objects.create_user(
            username="admin",
            email="admin@domusgestor.cat",
            nip="ADM001",
            password="DomusGestor2026!",
        )
        print("Usuari creat  →  NIP: ADM001 / Password: DomusGestor2026!")

    # ── Netejar dades existents ──────────────────────────────────────────────
    deleted_p = PagamentReserva.objects.all().delete()[0]
    deleted_r = ReservaBasica.objects.all().delete()[0]
    deleted_per = Persona.objects.all().delete()[0]
    deleted_m = Immoble.objects.all().delete()[0]
    deleted_s = Servei.objects.all().delete()[0]
    deleted_t = Temporada.objects.all().delete()[0]
    print(f"Eliminats: {deleted_p} pagaments, {deleted_r} reserves, {deleted_per} persones, {deleted_m} immobles, {deleted_s} serveis, {deleted_t} temporades")

    # ── 20 Immobles ─────────────────────────────────────────────────────────
    immobles_data = [
        ("Apartament Gracia Centre",  "DG-001", "Carrer de Verdi, 32, 1r 2a",       "Barcelona",        "08012", "Pis",        4, 2, 1,  85,  110.00, True,  "Joan Serra Pujol",    "12345678A", "joan.serra@gmail.com",    "+34 600 111 222", "Carrer Major, 5, Barcelona",          "ES21 2100 0418 4502 0005 1332"),
        ("Atic Vista Mar",            "DG-002", "Passeig de Gracia, 80, Atic",       "Barcelona",        "08008", "Atic",       2, 1, 1,  65,  220.00, True,  "Marta Vidal Puig",    "87654321B", "marta.vidal@hotmail.com", "+34 611 222 333", "Via Laietana, 20, Barcelona",         "ES80 2038 0509 7032 0020 0020"),
        ("Casa amb jardi Sitges",     "DG-003", "Carrer Sant Pau, 14",               "Sitges",           "08870", "Casa",       8, 4, 2, 200,  350.00, True,  "Pau Mas Roca",        "11223344C", "pau.mas@outlook.com",     "+34 622 333 444", "Rambla de Catalunya, 10, Sitges",     "ES91 2100 0418 6702 0015 1236"),
        ("Estudi Barceloneta",        "DG-004", "Carrer de la Barceloneta, 5, 2n",   "Barcelona",        "08003", "Estudi",     2, 0, 1,  28,   75.00, True,  "Anna Ferrer Costa",   "22334455D", "anna.ferrer@gmail.com",   "+34 633 444 555", "Avinguda Mistral, 3, Barcelona",      "ES76 0049 0001 5021 3400 1234"),
        ("Xalet Costa Brava",         "DG-005", "Avinguda de la Platja, 8",          "Lloret de Mar",    "17310", "Xalet",     10, 5, 3, 320,  480.00, True,  "Enric Bosch Torres",  "33445566E", "enric.bosch@empresa.cat", "+34 644 555 666", "Carrer Nou, 22, Girona",              "ES58 2100 0418 5814 0012 3456"),
        ("Pis Modern Eixample",       "DG-006", "Carrer de Muntaner, 210, 3r 1a",    "Barcelona",        "08036", "Pis",        4, 2, 1,  90,  150.00, True,  "Rosa Gines Llop",     "44556677F", "rosa.gines@yahoo.es",     "+34 655 666 777", "Carrer Arago, 45, Barcelona",         "ES93 0081 0205 3080 0600 0078"),
        ("Apartament Girona Vella",   "DG-007", "Carrer de la Forca, 7, 1r",         "Girona",           "17004", "Pis",        3, 2, 1,  75,   95.00, True,  "Miquel Soler Pla",    "55667788G", "miquel.soler@gmail.com",  "+34 666 777 888", "Placa Catalunya, 1, Girona",          "ES12 2100 0418 6702 0015 9999"),
        ("Duplex Tarragona Mar",      "DG-008", "Passeig Maritim, 55, 1r 1a",        "Tarragona",        "43004", "Duplex",     5, 3, 2, 120,  180.00, True,  "Laia Camprubi Mir",   "66778899H", "laia.camp@correu.cat",    "+34 677 888 999", "Rambla Nova, 8, Tarragona",           "ES79 2100 0418 6202 0037 1234"),
        ("Casa Rural Osona",          "DG-009", "Cami de les Fonts, s/n",            "Vic",              "08500", "Casa Rural",12, 5, 3, 350,  300.00, True,  "Francesc Puig Vall",  "77889900I", "fpuig@ruralcat.net",      "+34 688 999 000", "Placa Major, 3, Vic",                 "ES96 2100 0418 5614 0099 0012"),
        ("Apartament Lleida Centre",  "DG-010", "Carrer Major, 45, 2n 3a",           "Lleida",           "25002", "Pis",        4, 2, 1,  80,   70.00, True,  "Nuria Gomez Sola",    "88990011J", "nuria.gomez@gmail.com",   "+34 699 000 111", "Rambla Ferran, 12, Lleida",           "ES33 2100 0418 6202 0011 2233"),
        ("Atic Terrassa Vista",       "DG-011", "Carrer de la Rasa, 10, Atic",       "Terrassa",         "08221", "Atic",       3, 2, 1,  95,  130.00, True,  "Josep Claret Font",   "99001122K", "jclaret@terrassa.org",    "+34 600 123 456", "Carrer Colom, 5, Terrassa",           "ES67 2100 0418 5214 0022 3344"),
        ("Pis Badalona Platja",       "DG-012", "Avinguda del Maresme, 120, 1r 2a",  "Badalona",         "08915", "Pis",        5, 3, 2, 100,  120.00, True,  "Carles Valls Prat",   "10203040L", "cvalls@gmail.com",        "+34 611 234 567", "Carrer Mar, 18, Badalona",            "ES55 2100 0418 4702 0033 4455"),
        ("Casa Adossada Sabadell",    "DG-013", "Carrer dels Pins, 23",              "Sabadell",         "08205", "Casa",       6, 3, 2, 150,  160.00, False, "Montserrat Riba Mas", "20304050M", "mriba@sabadell.cat",      "+34 622 345 678", "Avinguda Catalunya, 30, Sabadell",    "ES44 2100 0418 4502 0044 5566"),
        ("Estudi Mataro Rambla",      "DG-014", "La Rambla, 88, 3r 1a",              "Mataro",           "08302", "Estudi",     2, 1, 1,  40,   65.00, True,  "Dolors Pont Coma",    "30405060N", "dpont@mataro.net",        "+34 633 456 789", "Carrer Nou, 5, Mataro",               "ES88 2100 0418 4302 0055 6677"),
        ("Apartament Manresa Nou",    "DG-015", "Carrer del Bruc, 34, 4t 2a",        "Manresa",          "08240", "Pis",        3, 2, 1,  70,   80.00, True,  "Ricard Torras Mas",   "40506070O", "rtorras@manresa.cat",     "+34 644 567 890", "Placa Major, 2, Manresa",             "ES22 2100 0418 4102 0066 7788"),
        ("Xalet Roses Costa",         "DG-016", "Avinguda de Rhode, 15",             "Roses",            "17480", "Xalet",      8, 4, 2, 240,  400.00, True,  "Silvia Compte Ros",   "50607080P", "scompte@roses.org",       "+34 655 678 901", "Carrer Pescadors, 3, Roses",          "ES66 2100 0418 3902 0077 8899"),
        ("Pis Figueres Rambla",       "DG-017", "La Rambla, 55, 2n 1a",              "Figueres",         "17600", "Pis",        4, 2, 1,  85,   85.00, True,  "Jordi Pages Olive",   "60708090Q", "jpages@figueres.cat",     "+34 666 789 012", "Carrer Nou, 10, Figueres",            "ES55 2100 0418 3702 0088 9900"),
        ("Casa Rural Priorat",        "DG-018", "Carretera de la Serra, km 3",       "Falset",           "43730", "Casa Rural",10, 4, 2, 280,  260.00, True,  "Merce Angles Bru",    "70809010R", "mangles@priorat.org",     "+34 677 890 123", "Placa de la Quartera, 1, Falset",     "ES44 2100 0418 3502 0099 0011"),
        ("Apartament Tortosa Riu",    "DG-019", "Passeig de l Ebre, 22, 3r 2a",      "Tortosa",          "43500", "Pis",        4, 2, 1,  80,   75.00, True,  "Xavier Clua Ferre",   "80901020S", "xclua@tortosa.net",       "+34 688 901 234", "Carrer de la Rosa, 7, Tortosa",       "ES33 2100 0418 3302 0100 1122"),
        ("Duplex Vilanova Centre",    "DG-020", "Carrer de la Unio, 12, 1r 1a",      "Vilanova i la G.", "08800", "Duplex",     6, 3, 2, 140,  195.00, True,  "Teresa Oliveras Pou", "90101030T", "toliveras@vilanova.cat",  "+34 699 012 345", "Rambla de la Pau, 4, Vilanova",       "ES11 2100 0418 3102 0111 2233"),
    ]

    fotos_per_immoble = [
        ["https://placehold.co/800x600?text=DG-001-1", "https://placehold.co/800x600?text=DG-001-2", "https://placehold.co/800x600?text=DG-001-3"],
        ["https://placehold.co/800x600?text=DG-002-1", "https://placehold.co/800x600?text=DG-002-2", "https://placehold.co/800x600?text=DG-002-3", "https://placehold.co/800x600?text=DG-002-4"],
        ["https://placehold.co/800x600?text=DG-003-1", "https://placehold.co/800x600?text=DG-003-2", "https://placehold.co/800x600?text=DG-003-3", "https://placehold.co/800x600?text=DG-003-4", "https://placehold.co/800x600?text=DG-003-5"],
        ["https://placehold.co/800x600?text=DG-004-1", "https://placehold.co/800x600?text=DG-004-2"],
        ["https://placehold.co/800x600?text=DG-005-1", "https://placehold.co/800x600?text=DG-005-2", "https://placehold.co/800x600?text=DG-005-3", "https://placehold.co/800x600?text=DG-005-4", "https://placehold.co/800x600?text=DG-005-5"],
        ["https://placehold.co/800x600?text=DG-006-1", "https://placehold.co/800x600?text=DG-006-2", "https://placehold.co/800x600?text=DG-006-3"],
        ["https://placehold.co/800x600?text=DG-007-1", "https://placehold.co/800x600?text=DG-007-2", "https://placehold.co/800x600?text=DG-007-3"],
        ["https://placehold.co/800x600?text=DG-008-1", "https://placehold.co/800x600?text=DG-008-2", "https://placehold.co/800x600?text=DG-008-3", "https://placehold.co/800x600?text=DG-008-4"],
        ["https://placehold.co/800x600?text=DG-009-1", "https://placehold.co/800x600?text=DG-009-2", "https://placehold.co/800x600?text=DG-009-3", "https://placehold.co/800x600?text=DG-009-4", "https://placehold.co/800x600?text=DG-009-5"],
        ["https://placehold.co/800x600?text=DG-010-1", "https://placehold.co/800x600?text=DG-010-2"],
        ["https://placehold.co/800x600?text=DG-011-1", "https://placehold.co/800x600?text=DG-011-2", "https://placehold.co/800x600?text=DG-011-3"],
        ["https://placehold.co/800x600?text=DG-012-1", "https://placehold.co/800x600?text=DG-012-2", "https://placehold.co/800x600?text=DG-012-3", "https://placehold.co/800x600?text=DG-012-4"],
        ["https://placehold.co/800x600?text=DG-013-1", "https://placehold.co/800x600?text=DG-013-2", "https://placehold.co/800x600?text=DG-013-3"],
        ["https://placehold.co/800x600?text=DG-014-1", "https://placehold.co/800x600?text=DG-014-2"],
        ["https://placehold.co/800x600?text=DG-015-1", "https://placehold.co/800x600?text=DG-015-2", "https://placehold.co/800x600?text=DG-015-3"],
        ["https://placehold.co/800x600?text=DG-016-1", "https://placehold.co/800x600?text=DG-016-2", "https://placehold.co/800x600?text=DG-016-3", "https://placehold.co/800x600?text=DG-016-4", "https://placehold.co/800x600?text=DG-016-5"],
        ["https://placehold.co/800x600?text=DG-017-1", "https://placehold.co/800x600?text=DG-017-2", "https://placehold.co/800x600?text=DG-017-3"],
        ["https://placehold.co/800x600?text=DG-018-1", "https://placehold.co/800x600?text=DG-018-2", "https://placehold.co/800x600?text=DG-018-3", "https://placehold.co/800x600?text=DG-018-4"],
        ["https://placehold.co/800x600?text=DG-019-1", "https://placehold.co/800x600?text=DG-019-2", "https://placehold.co/800x600?text=DG-019-3"],
        ["https://placehold.co/800x600?text=DG-020-1", "https://placehold.co/800x600?text=DG-020-2", "https://placehold.co/800x600?text=DG-020-3", "https://placehold.co/800x600?text=DG-020-4"],
    ]

    neteja_per_immoble = [
        (3, 2, 2), (2, 1, 2), (5, 3, 4), (1, 1, 1), (7, 4, 5),
        (3, 2, 2), (2, 2, 2), (4, 3, 3), (8, 5, 6), (3, 2, 2),
        (3, 2, 2), (3, 2, 3), (4, 3, 3), (1, 1, 1), (2, 2, 2),
        (6, 4, 5), (3, 2, 2), (6, 4, 5), (3, 2, 2), (4, 3, 3),
    ]

    horaris_per_immoble = [
        ("15:00", "21:00", "07:00", "11:00"), ("16:00", "21:00", "08:00", "11:00"),
        ("16:00", "20:00", "09:00", "12:00"), ("15:00", "22:00", "07:00", "11:00"),
        ("17:00", "21:00", "09:00", "12:00"), ("15:00", "21:00", "08:00", "11:00"),
        ("15:00", "20:00", "08:00", "11:00"), ("16:00", "21:00", "09:00", "12:00"),
        ("17:00", "20:00", "09:00", "12:00"), ("14:00", "20:00", "08:00", "11:00"),
        ("15:00", "21:00", "08:00", "11:00"), ("16:00", "21:00", "08:00", "11:00"),
        ("15:00", "20:00", "08:00", "11:00"), ("15:00", "21:00", "07:00", "11:00"),
        ("14:00", "20:00", "08:00", "11:00"), ("17:00", "21:00", "09:00", "12:00"),
        ("15:00", "20:00", "08:00", "11:00"), ("17:00", "20:00", "09:00", "12:00"),
        ("15:00", "23:00", "07:00", "11:00"), ("16:00", "21:00", "08:00", "12:00"),
    ]

    immobles = []
    for row, fotos, horaris, neteja in zip(immobles_data, fotos_per_immoble, horaris_per_immoble, neteja_per_immoble):
        (nom, ref, adr, ciutat, cp, tipus, cap, hab, banys, m2, preu, actiu,
         prop_nom, prop_dni, prop_email, prop_tel, prop_adr, prop_iban) = row
        ci_inici, ci_fi, co_inici, co_fi = horaris
        n_tanc, n_canvi, n_ober = neteja
        propietari = Persona.objects.create(
            nom_complet=prop_nom, dni_passaport=prop_dni, email=prop_email,
            telefon=prop_tel, residencia=prop_adr,
        )
        PerfilPropietari.objects.create(persona=propietari, iban=prop_iban, adreca_facturacio=prop_adr)
        imm = Immoble.objects.create(
            nom_comercial=nom, referencia=ref, adreca=adr, ciutat=ciutat,
            codi_postal=cp, tipus_immoble=tipus, capacitat_maxima=cap,
            num_habitacions=hab, num_banys=banys, metres_quadrats=m2,
            preu_base_nit=preu, actiu=actiu, propietari=propietari, fotos=fotos,
            hora_checkin_inici=ci_inici, hora_checkin_fi=ci_fi,
            hora_checkout_inici=co_inici, hora_checkout_fi=co_fi,
            neteja_tancament=n_tanc, neteja_canvi=n_canvi, neteja_obertura=n_ober,
        )
        immobles.append(imm)

    print(f"{len(immobles)} immobles creats")

    # ── Serveis ──────────────────────────────────────────────────────────────
    serveis_data = [
        ("Aire acondicionat", "AirVent", "climatitzacio"), ("Calefaccio", "Flame", "climatitzacio"),
        ("Ventilador de sostre", "Fan", "climatitzacio"), ("WiFi", "Wifi", "conectivitat"),
        ("TV pantalla plana", "Tv", "conectivitat"), ("Netflix", "MonitorPlay", "conectivitat"),
        ("Rentadora", "WashingMachine", "electrodomestics"), ("Assecadora", "Wind", "electrodomestics"),
        ("Rentavaixelles", "Sparkles", "electrodomestics"), ("Cuina totalment equipada", "ChefHat", "electrodomestics"),
        ("Microones", "Microwave", "electrodomestics"), ("Cafetera", "Coffee", "electrodomestics"),
        ("Planxa i taula de planxar", "Shirt", "electrodomestics"), ("Piscina", "Waves", "exterior"),
        ("Jardi privat", "TreePine", "exterior"), ("Terrassa", "Armchair", "exterior"),
        ("Barbacoa", "Drumstick", "exterior"), ("Aparcament gratuit", "Car", "exterior"),
        ("Garatge privat", "Warehouse", "exterior"), ("Ascensor", "ArrowUpDown", "altres"),
        ("Caixa forta", "Lock", "altres"), ("Admeten mascotes", "Dog", "altres"),
        ("Acces adaptat", "Accessibility", "altres"), ("Llencols inclosos", "Bed", "altres"),
        ("Tovalloles incloses", "Bath", "altres"), ("Bressol disponible", "Baby", "altres"),
        ("Check-in autonom", "Key", "altres"),
    ]

    serveis_obj = {}
    for nom, icona, categoria in serveis_data:
        s = Servei.objects.create(nom=nom, icona=icona, categoria=categoria)
        serveis_obj[nom] = s

    print(f"{len(serveis_obj)} serveis creats")

    assignacions = [
        ["WiFi", "Aire acondicionat", "Calefaccio", "Rentadora", "TV pantalla plana", "Cuina totalment equipada", "Ascensor", "Llencols inclosos", "Tovalloles incloses"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Terrassa", "TV pantalla plana", "Netflix", "Cuina totalment equipada", "Rentadora", "Ascensor", "Llencols inclosos"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Piscina", "Jardi privat", "Barbacoa", "Rentadora", "Assecadora", "Rentavaixelles", "TV pantalla plana", "Cuina totalment equipada", "Aparcament gratuit", "Admeten mascotes", "Llencols inclosos", "Tovalloles incloses"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "TV pantalla plana", "Cuina totalment equipada", "Microones", "Cafetera", "Ascensor"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Piscina", "Jardi privat", "Barbacoa", "Terrassa", "Rentadora", "Assecadora", "Rentavaixelles", "Cuina totalment equipada", "TV pantalla plana", "Netflix", "Aparcament gratuit", "Garatge privat", "Admeten mascotes", "Bressol disponible", "Caixa forta"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Rentadora", "Rentavaixelles", "TV pantalla plana", "Netflix", "Cuina totalment equipada", "Planxa i taula de planxar", "Ascensor", "Llencols inclosos", "Tovalloles incloses", "Cafetera"],
        ["WiFi", "Calefaccio", "TV pantalla plana", "Cuina totalment equipada", "Rentadora", "Ascensor", "Llencols inclosos", "Microones"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Terrassa", "TV pantalla plana", "Rentadora", "Cuina totalment equipada", "Aparcament gratuit", "Llencols inclosos", "Admeten mascotes", "Barbacoa"],
        ["WiFi", "Calefaccio", "Piscina", "Jardi privat", "Barbacoa", "Rentadora", "Assecadora", "Cuina totalment equipada", "TV pantalla plana", "Aparcament gratuit", "Admeten mascotes", "Bressol disponible", "Check-in autonom", "Ventilador de sostre"],
        ["WiFi", "Calefaccio", "TV pantalla plana", "Cuina totalment equipada", "Rentadora", "Ascensor", "Microones", "Cafetera"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Terrassa", "TV pantalla plana", "Netflix", "Rentadora", "Cuina totalment equipada", "Ascensor", "Planxa i taula de planxar"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Terrassa", "TV pantalla plana", "Rentadora", "Rentavaixelles", "Cuina totalment equipada", "Aparcament gratuit", "Llencols inclosos", "Tovalloles incloses"],
        ["WiFi", "Calefaccio", "Jardi privat", "TV pantalla plana", "Rentadora", "Cuina totalment equipada", "Garatge privat", "Admeten mascotes"],
        ["WiFi", "Aire acondicionat", "TV pantalla plana", "Cuina totalment equipada", "Microones", "Cafetera", "Ascensor"],
        ["WiFi", "Calefaccio", "TV pantalla plana", "Rentadora", "Cuina totalment equipada", "Ascensor", "Llencols inclosos", "Planxa i taula de planxar"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Piscina", "Jardi privat", "Barbacoa", "Terrassa", "Rentadora", "Assecadora", "Cuina totalment equipada", "TV pantalla plana", "Netflix", "Aparcament gratuit", "Admeten mascotes", "Caixa forta", "Llencols inclosos", "Tovalloles incloses"],
        ["WiFi", "Calefaccio", "TV pantalla plana", "Rentadora", "Cuina totalment equipada", "Ascensor", "Planxa i taula de planxar", "Microones"],
        ["WiFi", "Calefaccio", "Jardi privat", "Barbacoa", "Rentadora", "Assecadora", "Cuina totalment equipada", "TV pantalla plana", "Aparcament gratuit", "Admeten mascotes", "Bressol disponible", "Ventilador de sostre"],
        ["WiFi", "Calefaccio", "TV pantalla plana", "Cuina totalment equipada", "Rentadora", "Ascensor", "Check-in autonom", "Microones"],
        ["WiFi", "Aire acondicionat", "Calefaccio", "Terrassa", "TV pantalla plana", "Netflix", "Rentadora", "Rentavaixelles", "Cuina totalment equipada", "Aparcament gratuit", "Llencols inclosos", "Tovalloles incloses"],
    ]

    for imm, noms_serveis in zip(immobles, assignacions):
        imm.serveis.set([serveis_obj[nom] for nom in noms_serveis])

    print("Serveis assignats als immobles")

    # ── Temporades ───────────────────────────────────────────────────────────
    temporades_data = [
        (0, "Temporada Baixa",      "2000-01-01", "2000-03-31",  90.00, 2, [], 10.00),
        (0, "Temporada Mitja",      "2000-04-01", "2000-06-30", 110.00, 3, [], 15.00),
        (0, "Temporada Alta",       "2000-07-01", "2000-08-31", 155.00, 3, [], 20.00),
        (0, "Temporada Mitja Tard", "2000-09-01", "2000-12-31", 105.00, 2, [], 15.00),
        (1, "Temporada Baixa",      "2000-01-01", "2000-05-31", 180.00, 2, [], 15.00),
        (1, "Temporada Alta",       "2000-06-01", "2000-09-15", 280.00, 3, [], 20.00),
        (1, "Temporada Mitja",      "2000-09-16", "2000-12-31", 210.00, 2, [], 15.00),
        (2, "Hivern",               "2000-01-01", "2000-03-31", 270.00, 2, [], 10.00),
        (2, "Primavera",            "2000-04-01", "2000-06-30", 340.00, 3, [], 15.00),
        (2, "Estiu",                "2000-07-01", "2000-08-31", 480.00, 7, [5, 6], 20.00),
        (2, "Tardor",               "2000-09-01", "2000-12-31", 310.00, 3, [], 10.00),
        (3, "Temporada Baixa",      "2000-01-01", "2000-06-14",  65.00, 2, [], 10.00),
        (3, "Temporada Alta",       "2000-06-15", "2000-09-15",  95.00, 3, [], 15.00),
        (3, "Temporada Baixa",      "2000-09-16", "2000-12-31",  65.00, 2, [], 10.00),
        (4, "Temporada Baixa",      "2000-01-01", "2000-03-31", 360.00, 2, [], 10.00),
        (4, "Setmana Santa",        "2000-04-01", "2000-04-12", 520.00, 5, [5, 6], 20.00),
        (4, "Primavera/Tardor",     "2000-04-13", "2000-06-30", 420.00, 3, [], 15.00),
        (4, "Temporada Alta",       "2000-07-01", "2000-08-31", 650.00, 7, [5, 6], 20.00),
        (4, "Tardor/Hivern",        "2000-09-01", "2000-12-31", 400.00, 3, [], 15.00),
        (5, "Temporada Baixa",      "2000-01-01", "2000-03-31", 120.00, 2, [], 10.00),
        (5, "Temporada Mitja",      "2000-04-01", "2000-06-30", 150.00, 3, [], 15.00),
        (5, "Temporada Alta",       "2000-07-01", "2000-08-31", 195.00, 3, [], 18.00),
        (5, "Temporada Mitja Tard", "2000-09-01", "2000-12-31", 140.00, 2, [], 15.00),
        (6, "Hivern",               "2000-01-01", "2000-05-31",  80.00, 2, [], 10.00),
        (6, "Estiu",                "2000-06-01", "2000-09-30", 115.00, 3, [], 18.00),
        (6, "Tardor/Hivern",        "2000-10-01", "2000-12-31",  80.00, 2, [], 10.00),
        (7, "Temporada Baixa",      "2000-01-01", "2000-05-31", 145.00, 2, [], 12.00),
        (7, "Temporada Alta",       "2000-06-01", "2000-09-15", 230.00, 7, [5, 6], 18.00),
        (7, "Temporada Baixa",      "2000-09-16", "2000-12-31", 145.00, 2, [], 12.00),
        (8, "Hivern",               "2000-01-01", "2000-03-31", 240.00, 2, [], 15.00),
        (8, "Primavera",            "2000-04-01", "2000-06-30", 290.00, 3, [5], 15.00),
        (8, "Estiu",                "2000-07-01", "2000-08-31", 380.00, 7, [5, 6], 20.00),
        (8, "Tardor",               "2000-09-01", "2000-12-31", 260.00, 3, [], 15.00),
        (9, "Temporada Baixa",      "2000-01-01", "2000-06-30",  60.00, 2, [], 10.00),
        (9, "Temporada Alta",       "2000-07-01", "2000-08-31",  85.00, 3, [], 15.00),
        (9, "Temporada Baixa",      "2000-09-01", "2000-12-31",  60.00, 2, [], 10.00),
        (10, "Temporada Baixa",     "2000-01-01", "2000-05-31", 105.00, 2, [], 12.00),
        (10, "Temporada Alta",      "2000-06-01", "2000-09-15", 165.00, 3, [], 18.00),
        (10, "Temporada Baixa",     "2000-09-16", "2000-12-31", 105.00, 2, [], 12.00),
        (11, "Temporada Baixa",     "2000-01-01", "2000-05-31",  95.00, 2, [], 10.00),
        (11, "Temporada Alta",      "2000-06-01", "2000-09-15", 155.00, 7, [5, 6], 20.00),
        (11, "Temporada Mitja",     "2000-09-16", "2000-12-31", 110.00, 3, [], 15.00),
        (12, "Temporada Baixa",     "2000-01-01", "2000-06-30", 130.00, 2, [], 10.00),
        (12, "Temporada Alta",      "2000-07-01", "2000-08-31", 190.00, 3, [], 15.00),
        (12, "Temporada Baixa",     "2000-09-01", "2000-12-31", 130.00, 2, [], 10.00),
        (13, "Temporada Baixa",     "2000-01-01", "2000-06-14",  55.00, 2, [], 10.00),
        (13, "Temporada Alta",      "2000-06-15", "2000-09-15",  80.00, 7, [5, 6], 15.00),
        (13, "Temporada Baixa",     "2000-09-16", "2000-12-31",  55.00, 2, [], 10.00),
        (14, "Temporada Unica",     "2000-01-01", "2000-12-31",  80.00, 2, [], 10.00),
        (15, "Hivern",              "2000-01-01", "2000-03-31", 300.00, 2, [], 15.00),
        (15, "Setmana Santa",       "2000-04-01", "2000-04-12", 450.00, 5, [5, 6], 20.00),
        (15, "Primavera",           "2000-04-13", "2000-06-30", 380.00, 3, [], 15.00),
        (15, "Temporada Alta",      "2000-07-01", "2000-08-31", 560.00, 7, [5, 6], 20.00),
        (15, "Tardor/Hivern",       "2000-09-01", "2000-12-31", 350.00, 3, [], 15.00),
        (16, "Temporada Baixa",     "2000-01-01", "2000-06-30",  70.00, 2, [], 10.00),
        (16, "Temporada Alta",      "2000-07-01", "2000-08-31", 105.00, 3, [], 15.00),
        (16, "Temporada Baixa",     "2000-09-01", "2000-12-31",  70.00, 2, [], 10.00),
        (17, "Hivern",              "2000-01-01", "2000-03-31", 200.00, 2, [], 15.00),
        (17, "Primavera/Tardor",    "2000-04-01", "2000-06-30", 250.00, 3, [5], 15.00),
        (17, "Estiu",               "2000-07-01", "2000-08-31", 330.00, 7, [5, 6], 20.00),
        (17, "Tardor",              "2000-09-01", "2000-12-31", 220.00, 3, [], 15.00),
        (18, "Temporada Baixa",     "2000-01-01", "2000-06-30",  65.00, 2, [], 10.00),
        (18, "Temporada Alta",      "2000-07-01", "2000-08-31",  90.00, 3, [], 15.00),
        (18, "Temporada Baixa",     "2000-09-01", "2000-12-31",  65.00, 2, [], 10.00),
        (19, "Temporada Baixa",     "2000-01-01", "2000-05-31", 155.00, 2, [], 15.00),
        (19, "Temporada Alta",      "2000-06-01", "2000-09-15", 245.00, 7, [5, 6], 20.00),
        (19, "Temporada Mitja",     "2000-09-16", "2000-12-31", 180.00, 3, [], 15.00),
    ]

    temporades = [
        Temporada.objects.create(
            immoble=immobles[idx], nom=nom, data_inici=inici, data_fi=fi,
            preu_nit=preu, min_nits=min_nits, dies_checkin=dies_checkin, comissio=comissio,
        )
        for idx, nom, inici, fi, preu, min_nits, dies_checkin, comissio in temporades_data
    ]
    print(f"{len(temporades)} temporades creades")

    # ── 50 Inquilins ─────────────────────────────────────────────────────────
    # fmt: (nom, dni, email, residencia)
    inquilins_data = [
        # originals 0-19
        ("Marc Rovira Puig",      "98765432A", "marc.rovira@gmail.com",    "Carrer Major, 5, Barcelona"),
        ("Laia Font Soler",       "87654321X", "laia.font@hotmail.com",    "Avinguda Diagonal, 10, Barcelona"),
        ("Jordi Mestre Valls",    "76543210C", "jmestre@outlook.com",      "Carrer Nou, 3, Girona"),
        ("Silvia Soler Puig",     "65432109D", "silvia.soler@gmail.com",   "Placa Catalunya, 8, Tarragona"),
        ("Pere Mas Bosch",        "54321098E", "pere.mas@correu.cat",      "Carrer del Pi, 12, Lleida"),
        ("Neus Casas Tort",       "43210987F", "neus.casas@yahoo.es",      "Rambla Nova, 20, Tarragona"),
        ("Albert Prat Gomez",     "32109876G", "albert.prat@gmail.com",    "Carrer Balmes, 55, Barcelona"),
        ("Montse Ribes Clar",     "21098765H", "mribes@empresa.cat",       "Via Augusta, 3, Barcelona"),
        ("Raul Ferrer Jove",      "10987654I", "rferrer@gmail.com",        "Carrer Groc, 7, Reus"),
        ("Carme Vila Mas",        "09876543J", "cvilam@terra.es",          "Passeig de la Pau, 1, Vic"),
        ("Tomas Puigdomenech",    "98765043K", "tpuig@gmail.com",          "Carrer dels Albers, 4, Manresa"),
        ("Gema Llorens Fite",     "87654032L", "gllorens@hotmail.com",     "Placa de la Vila, 2, Sabadell"),
        ("Isidre Camps Ros",      "76543021M", "icamps@empresa.net",       "Carrer del Carme, 18, Terrassa"),
        ("Roser Nogues Badia",    "65432010N", "rnogues@gmail.com",        "Avinguda Roma, 6, Figueres"),
        ("Felip Bruges Cos",      "54321009O", "fbruguesc@outlook.com",    "Carrer Palau, 9, Roses"),
        ("Olga Sala Torra",       "43210908P", "osala@gmail.com",          "Carrer Victoria, 14, Badalona"),
        ("Raimon Coll Barnils",   "32109807Q", "rcoll@correu.cat",         "Rambla Ferran, 33, Lleida"),
        ("Imma Domenec Rius",     "21098706R", "idomr@terra.es",           "Carrer Ample, 21, Tortosa"),
        ("Berta Farres Vila",     "10987605S", "bfarres@gmail.com",        "Carrer del Comerc, 5, Vilanova"),
        ("Lluc Alsina Pont",      "09876504T", "lalsina@gmail.com",        "Carrer Verdaguer, 11, Mataro"),
        # nous 20-49
        ("David Torra Camps",     "A1234567B", "dtorra@gmail.com",         "Carrer Ample, 10, Barcelona"),
        ("Marina Planas Bech",    "B2345678C", "mplanas@hotmail.com",      "Avinguda Meridiana, 45, Barcelona"),
        ("Oriol Casas Forn",      "C3456789D", "ocasas@outlook.com",       "Carrer Nou, 8, Sabadell"),
        ("Cristina Molina Riera", "D4567890E", "cmolina@gmail.com",        "Placa Major, 3, Vic"),
        ("Sergi Esteve Folch",    "E5678901F", "sesteve@correu.cat",       "Carrer Balmes, 12, Terrassa"),
        ("Montse Coma Besa",      "F6789012G", "mcoma@gmail.com",          "Rambla Catalunya, 22, Girona"),
        ("Pau Carreras Tort",     "G7890123H", "pcarreras@empresa.cat",    "Carrer Nou, 5, Lleida"),
        ("Neus Viladrich Pons",   "H8901234I", "nviladrich@gmail.com",     "Avinguda del Mar, 3, Sitges"),
        ("Victor Sanchez Roca",   "I9012345J", "vsanchez@yahoo.es",        "Carrer Amalia, 7, Roses"),
        ("Anna Pascual Ferre",    "J0123456K", "apascual@gmail.com",       "Passeig Maritim, 12, Badalona"),
        ("Miquel Miro Llopis",    "K1234560L", "mmiro@correu.cat",         "Carrer Major, 33, Figueres"),
        ("Laura Blanco Valls",    "L2345601M", "lblanco@gmail.com",        "Rambla del Pi, 5, Tortosa"),
        ("Carles Duran Mas",      "M3456012N", "cduran@hotmail.com",       "Carrer Groc, 14, Manresa"),
        ("Rosa Giralt Bou",       "N4560123O", "rgiralt@gmail.com",        "Avinguda Central, 9, Mataro"),
        ("Joaquim Tubert Vives",  "O5601234P", "jtubert@empresa.net",      "Carrer dels Pins, 2, Vilanova"),
        ("Marta Garriga Cors",    "P6012345Q", "mgarriga@gmail.com",       "Carrer Olot, 18, Olot"),
        ("Ricard Pujol Costa",    "Q0123456R", "rpujol@correu.cat",        "Carrer Llevant, 3, Tarragona"),
        ("Laia Ballester Pou",    "R1234067S", "lballester@gmail.com",     "Placa Independencia, 4, Girona"),
        ("Arnau Codina Puig",     "S2340678T", "acodina@outlook.com",      "Carrer Princesa, 6, Barcelona"),
        ("Gemma Torras Font",     "T3401789U", "gtorras@gmail.com",        "Carrer Amposta, 11, Tortosa"),
        ("Hector Cabane Mir",     "U4012890V", "hcabane@empresa.cat",      "Avinguda Diagonal, 88, Barcelona"),
        ("Pilar Espinal Pla",     "V0123901W", "pespinal@gmail.com",       "Carrer Mare de Deu, 5, Badalona"),
        ("Ferran Catala Bosc",    "W1230012X", "fcatala@hotmail.com",      "Carrer del Vent, 3, Roses"),
        ("Susanna Roca Fuste",    "X2301123Y", "sroca@gmail.com",          "Rambla Vella, 15, Tarragona"),
        ("Toni Angles Mur",       "Y3012234Z", "tangles@correu.cat",       "Carrer Nou, 20, Lloret de Mar"),
        ("Elena Verdaguer Pons",  "Z0123345A", "everdaguer@gmail.com",     "Carrer Foneria, 8, Sabadell"),
        ("Guillem Pallares Ros",  "A1234456B", "gpallares@gmail.com",      "Avinguda Pau Casals, 3, Barcelona"),
        ("Merce Tarrago Sala",    "B2345567C", "mtarrago@hotmail.com",     "Carrer Colon, 12, Reus"),
        ("Ivan Massana Vall",     "C3456678D", "imassana@gmail.com",       "Placa Ajuntament, 1, Berga"),
        ("Silvia Margalef Tort",  "D4567789E", "smargalef@empresa.cat",    "Carrer Anoia, 7, Igualada"),
    ]

    tots_inquilins = []
    for nom, dni, email, residencia in inquilins_data:
        inq = Persona.objects.create(nom_complet=nom, dni_passaport=dni, email=email, residencia=residencia)
        PerfilInquili.objects.create(persona=inq)
        tots_inquilins.append(inq)

    print(f"{len(tots_inquilins)} inquilins creats")

    # ── Reserves ─────────────────────────────────────────────────────────────
    # fmt: (imm_i, inq_i, entrada, sortida, pagat, tipus, lim_extra, comentaris, import_total, estat_reserva)
    # import_pagat = import_total si pagat=True, 0 si False
    # estat_pagament derivat de pagat i estat_reserva
    reserves_data = [
        # ── 2026 originals (20) ──────────────────────────────────────────────
        (0,  0,  "2026-01-10", "2026-01-15", True,  "Airbnb",  1, "Entrada abans de les 15:00 si es possible.",    525.00,  "lista"),
        (1,  1,  "2026-01-20", "2026-01-23", True,  "Booking", 0, "Hostes habituals, llits separats.",             540.00,  "lista"),
        (2,  2,  "2026-02-03", "2026-02-10", True,  "Direct",  2, "Reserva familiar, necessiten bressol.",        1890.00,  "lista"),
        (3,  3,  "2026-02-14", "2026-02-16", False, "Airbnb",  0, "Sant Valenti - decoracio especial.",            130.00,  "lista"),
        (4,  4,  "2026-03-01", "2026-03-08", True,  "Direct",  3, "Estada llarga, descompte aplicat.",            2520.00,  "lista"),
        (5,  5,  "2026-03-15", "2026-03-18", False, "Booking", 0, "",                                              360.00,  "lista"),
        (6,  6,  "2026-04-05", "2026-04-07", True,  "Airbnb",  1, "Cap d'any avancat - Setmana Santa.",           160.00,  "lista"),
        (7,  7,  "2026-04-20", "2026-04-25", False, "Direct",  0, "Pendent confirmacio pagament.",                 725.00,  "lista"),
        (8,  8,  "2026-05-01", "2026-05-05", True,  "Booking", 2, "Festa local, possible soroll.",               1160.00,  "lista"),
        (9,  9,  "2026-05-10", "2026-05-17", False, "Airbnb",  0, "",                                              420.00,  "lista"),
        (10, 10, "2026-05-20", "2026-05-22", True,  "Direct",  1, "Treball, necessita wifi rapid.",                210.00,  "lista"),
        (11, 11, "2026-06-01", "2026-06-08", False, "Booking", 0, "",                                            1085.00,  "reservada"),
        (12, 12, "2026-06-15", "2026-06-20", True,  "Airbnb",  2, "Aniversari de noces.",                         950.00,  "reservada"),
        (13, 13, "2026-07-01", "2026-07-07", False, "Altres",  0, "Reserva via partner extern.",                   480.00,  "prereservada"),
        (14, 14, "2026-07-10", "2026-07-14", True,  "Direct",  1, "",                                              320.00,  "prereservada"),
        (15, 15, "2026-07-20", "2026-07-27", False, "Booking", 2, "Mascota petita autoritzada.",                 3920.00,  "prereservada"),
        (16, 16, "2026-08-01", "2026-08-10", True,  "Airbnb",  3, "Vacances familiars d'estiu.",                   945.00,  "prereservada"),
        (17, 17, "2026-08-15", "2026-08-18", True,  "Direct",  0, "Pagat per transferencia.",                      990.00,  "prereservada"),
        (18, 18, "2026-09-01", "2026-09-05", False, "Booking", 1, "",                                              360.00,  "prereservada"),
        (19, 19, "2026-09-10", "2026-09-15", True,  "Airbnb",  2, "Check-in autonom amb codi.",                  1225.00,  "prereservada"),

        # ── 2024 (71 reserves) ───────────────────────────────────────────────
        # Febrer 2024
        (0,  20, "2024-02-05", "2024-02-08", True,  "Direct",  0, "",   270.00, "lista"),
        (5,  21, "2024-02-10", "2024-02-14", True,  "Booking", 0, "",   480.00, "lista"),
        (9,  22, "2024-02-12", "2024-02-15", True,  "Airbnb",  0, "",   180.00, "lista"),
        (14, 23, "2024-02-20", "2024-02-23", True,  "Direct",  0, "",   240.00, "lista"),
        (17, 24, "2024-02-22", "2024-02-25", True,  "Booking", 0, "",   600.00, "lista"),
        # Marc 2024
        (1,  25, "2024-03-01", "2024-03-04", True,  "Airbnb",  0, "",   540.00, "lista"),
        (6,  26, "2024-03-08", "2024-03-12", True,  "Direct",  0, "",   320.00, "lista"),
        (10, 27, "2024-03-15", "2024-03-18", True,  "Booking", 0, "",   315.00, "lista"),
        (15, 28, "2024-03-20", "2024-03-24", True,  "Direct",  0, "",  1200.00, "lista"),
        (18, 29, "2024-03-22", "2024-03-25", False, "Airbnb",  0, "",   195.00, "cancelada"),
        (3,  30, "2024-03-10", "2024-03-13", True,  "Booking", 0, "",   195.00, "lista"),
        # Abril 2024
        (4,  31, "2024-03-30", "2024-04-06", True,  "Direct",  2, "Setmana Santa familia",  3640.00, "lista"),
        (2,  32, "2024-04-01", "2024-04-06", True,  "Airbnb",  1, "Setmana Santa",          1700.00, "lista"),
        (16, 33, "2024-04-06", "2024-04-11", True,  "Booking", 0, "Setmana Santa Roses",    2250.00, "lista"),
        (8,  34, "2024-04-08", "2024-04-12", True,  "Direct",  0, "Setmana Santa rural",    1160.00, "lista"),
        (11, 35, "2024-04-15", "2024-04-20", True,  "Booking", 0, "",    475.00, "lista"),
        (7,  36, "2024-04-20", "2024-04-25", False, "Airbnb",  0, "",    725.00, "cancelada"),
        (0,  37, "2024-04-22", "2024-04-26", True,  "Direct",  0, "",    440.00, "lista"),
        (13, 38, "2024-04-25", "2024-04-28", True,  "Airbnb",  0, "",    165.00, "lista"),
        # Maig 2024
        (1,  39, "2024-05-01", "2024-05-05", True,  "Booking", 0, "",    720.00, "lista"),
        (5,  40, "2024-05-08", "2024-05-12", True,  "Direct",  0, "",    600.00, "lista"),
        (9,  41, "2024-05-15", "2024-05-18", True,  "Booking", 0, "",    180.00, "lista"),
        (15, 42, "2024-05-20", "2024-05-24", True,  "Direct",  0, "",   1520.00, "lista"),
        (3,  43, "2024-05-22", "2024-05-25", True,  "Airbnb",  0, "",    195.00, "lista"),
        (6,  44, "2024-05-25", "2024-05-29", True,  "Booking", 0, "",    320.00, "lista"),
        (19, 45, "2024-05-27", "2024-05-31", True,  "Direct",  0, "",    620.00, "lista"),
        (14, 46, "2024-05-28", "2024-05-31", True,  "Airbnb",  0, "",    240.00, "lista"),
        (12, 47, "2024-05-10", "2024-05-14", True,  "Booking", 0, "",    520.00, "lista"),
        # Juny 2024
        (4,  48, "2024-06-01", "2024-06-08", True,  "Direct",  2, "Grup familiar",  2940.00, "lista"),
        (2,  49, "2024-06-07", "2024-06-14", True,  "Airbnb",  1, "",   2380.00, "lista"),
        (7,  20, "2024-06-08", "2024-06-15", True,  "Booking", 0, "",   1610.00, "lista"),
        (0,  21, "2024-06-15", "2024-06-20", True,  "Direct",  0, "",    550.00, "lista"),
        (11, 22, "2024-06-15", "2024-06-22", True,  "Booking", 0, "",   1085.00, "lista"),
        (16, 23, "2024-06-21", "2024-06-28", True,  "Airbnb",  1, "",   2660.00, "lista"),
        (10, 24, "2024-06-22", "2024-06-25", True,  "Direct",  0, "",    495.00, "lista"),
        (13, 25, "2024-06-25", "2024-06-28", True,  "Airbnb",  0, "",    240.00, "lista"),
        (5,  26, "2024-06-28", "2024-07-02", True,  "Booking", 0, "",    600.00, "lista"),
        # Juliol 2024
        (4,  27, "2024-07-06", "2024-07-13", True,  "Direct",  3, "Familia nombrosa",  4550.00, "lista"),
        (16, 28, "2024-07-06", "2024-07-13", True,  "Airbnb",  2, "",   3920.00, "lista"),
        (2,  29, "2024-07-07", "2024-07-14", True,  "Direct",  2, "",   3360.00, "lista"),
        (8,  30, "2024-07-06", "2024-07-13", True,  "Booking", 1, "",   2660.00, "lista"),
        (15, 31, "2024-07-13", "2024-07-20", True,  "Direct",  2, "",   3920.00, "lista"),
        (7,  32, "2024-07-13", "2024-07-20", True,  "Airbnb",  0, "",   1610.00, "lista"),
        (1,  33, "2024-07-15", "2024-07-20", True,  "Booking", 0, "",   1400.00, "lista"),
        (11, 34, "2024-07-20", "2024-07-27", True,  "Airbnb",  1, "",   1085.00, "lista"),
        (3,  35, "2024-07-22", "2024-07-26", True,  "Direct",  0, "",    380.00, "lista"),
        (6,  36, "2024-07-25", "2024-07-29", True,  "Booking", 0, "",    460.00, "lista"),
        (17, 37, "2024-07-06", "2024-07-13", True,  "Direct",  1, "",   2310.00, "lista"),
        (18, 38, "2024-07-13", "2024-07-16", True,  "Airbnb",  0, "",    270.00, "lista"),
        # Agost 2024
        (4,  39, "2024-08-03", "2024-08-10", True,  "Direct",  3, "Estiu gran",  4550.00, "lista"),
        (16, 40, "2024-08-03", "2024-08-10", True,  "Booking", 2, "",   3920.00, "lista"),
        (2,  41, "2024-08-03", "2024-08-10", True,  "Airbnb",  2, "",   3360.00, "lista"),
        (15, 42, "2024-08-10", "2024-08-17", True,  "Direct",  2, "",   3920.00, "lista"),
        (8,  43, "2024-08-03", "2024-08-10", True,  "Booking", 1, "",   2660.00, "lista"),
        (9,  44, "2024-08-10", "2024-08-14", True,  "Airbnb",  0, "",    340.00, "lista"),
        (0,  45, "2024-08-15", "2024-08-20", True,  "Direct",  0, "",    775.00, "lista"),
        (5,  46, "2024-08-12", "2024-08-17", True,  "Booking", 0, "",    975.00, "lista"),
        (19, 47, "2024-08-17", "2024-08-24", True,  "Airbnb",  1, "",   1715.00, "lista"),
        (17, 48, "2024-08-10", "2024-08-17", True,  "Direct",  1, "",   2310.00, "lista"),
        # Setembre 2024
        (0,  49, "2024-09-05", "2024-09-09", True,  "Direct",  0, "",    420.00, "lista"),
        (2,  20, "2024-09-07", "2024-09-12", True,  "Airbnb",  1, "",   1550.00, "lista"),
        (6,  21, "2024-09-10", "2024-09-14", True,  "Booking", 0, "",    460.00, "lista"),
        (15, 22, "2024-09-06", "2024-09-13", True,  "Direct",  1, "",   2450.00, "lista"),
        (7,  23, "2024-09-14", "2024-09-18", True,  "Airbnb",  0, "",    580.00, "lista"),
        (11, 24, "2024-09-15", "2024-09-20", True,  "Booking", 0, "",    550.00, "lista"),
        # Octubre 2024
        (5,  25, "2024-10-05", "2024-10-09", True,  "Direct",  0, "",    560.00, "lista"),
        (9,  26, "2024-10-10", "2024-10-13", True,  "Airbnb",  0, "",    180.00, "lista"),
        (14, 27, "2024-10-15", "2024-10-18", True,  "Booking", 0, "",    240.00, "lista"),
        # Novembre 2024
        (0,  28, "2024-11-08", "2024-11-11", True,  "Direct",  0, "",    270.00, "lista"),
        (6,  29, "2024-11-15", "2024-11-18", True,  "Booking", 0, "",    240.00, "lista"),
        (10, 30, "2024-11-20", "2024-11-23", False, "Airbnb",  0, "",    315.00, "cancelada"),

        # ── 2025 (87 reserves) ───────────────────────────────────────────────
        # Gener 2025
        (5,  31, "2025-01-10", "2025-01-14", True,  "Direct",  0, "",    480.00, "lista"),
        (9,  32, "2025-01-15", "2025-01-18", True,  "Airbnb",  0, "",    180.00, "lista"),
        (14, 33, "2025-01-20", "2025-01-23", True,  "Booking", 0, "",    240.00, "lista"),
        (17, 34, "2025-01-08", "2025-01-11", True,  "Direct",  0, "",    600.00, "lista"),
        # Febrer 2025
        (0,  35, "2025-02-10", "2025-02-13", True,  "Airbnb",  0, "Sant Valenti",   270.00, "lista"),
        (1,  36, "2025-02-14", "2025-02-17", True,  "Booking", 0, "",    540.00, "lista"),
        (6,  37, "2025-02-20", "2025-02-24", True,  "Direct",  0, "",    320.00, "lista"),
        (10, 38, "2025-02-22", "2025-02-25", False, "Airbnb",  0, "",    315.00, "cancelada"),
        (18, 39, "2025-02-15", "2025-02-18", True,  "Booking", 0, "",    195.00, "lista"),
        # Marc 2025
        (2,  40, "2025-03-07", "2025-03-11", True,  "Direct",  1, "",   1080.00, "lista"),
        (4,  41, "2025-03-15", "2025-03-19", True,  "Booking", 0, "",   1440.00, "lista"),
        (8,  42, "2025-03-20", "2025-03-24", True,  "Direct",  0, "",    960.00, "lista"),
        (15, 43, "2025-03-22", "2025-03-26", True,  "Airbnb",  0, "",   1200.00, "lista"),
        (11, 44, "2025-03-10", "2025-03-14", True,  "Booking", 0, "",    380.00, "lista"),
        (7,  45, "2025-03-25", "2025-03-29", True,  "Direct",  0, "",    580.00, "lista"),
        # Abril 2025
        (4,  46, "2025-04-12", "2025-04-19", True,  "Direct",  2, "Setmana Santa",  3640.00, "lista"),
        (16, 47, "2025-04-12", "2025-04-17", True,  "Booking", 1, "Setmana Santa",  2250.00, "lista"),
        (2,  48, "2025-04-05", "2025-04-10", True,  "Airbnb",  1, "",   1700.00, "lista"),
        (0,  49, "2025-04-20", "2025-04-24", True,  "Direct",  0, "",    440.00, "lista"),
        (5,  20, "2025-04-22", "2025-04-26", True,  "Booking", 0, "",    600.00, "lista"),
        (9,  21, "2025-04-25", "2025-04-28", True,  "Airbnb",  0, "",    180.00, "lista"),
        (13, 22, "2025-04-10", "2025-04-13", True,  "Direct",  0, "",    165.00, "lista"),
        (18, 23, "2025-04-15", "2025-04-19", True,  "Booking", 0, "",    260.00, "lista"),
        # Maig 2025
        (1,  24, "2025-05-03", "2025-05-07", True,  "Direct",  0, "",    720.00, "lista"),
        (3,  25, "2025-05-10", "2025-05-13", True,  "Airbnb",  0, "",    195.00, "lista"),
        (7,  26, "2025-05-15", "2025-05-19", True,  "Booking", 0, "",    580.00, "lista"),
        (15, 27, "2025-05-20", "2025-05-24", True,  "Direct",  1, "",   1520.00, "lista"),
        (17, 28, "2025-05-08", "2025-05-12", True,  "Airbnb",  0, "",   1000.00, "lista"),
        (19, 29, "2025-05-22", "2025-05-27", True,  "Booking", 0, "",    775.00, "lista"),
        (6,  30, "2025-05-25", "2025-05-29", True,  "Direct",  0, "",    320.00, "lista"),
        (10, 31, "2025-05-15", "2025-05-18", False, "Airbnb",  0, "",    315.00, "cancelada"),
        (14, 32, "2025-05-20", "2025-05-23", True,  "Booking", 0, "",    240.00, "lista"),
        # Juny 2025
        (4,  33, "2025-06-07", "2025-06-14", True,  "Direct",  2, "",   2940.00, "lista"),
        (2,  34, "2025-06-07", "2025-06-14", True,  "Airbnb",  1, "",   2380.00, "lista"),
        (16, 35, "2025-06-07", "2025-06-14", True,  "Booking", 1, "",   2660.00, "lista"),
        (8,  36, "2025-06-14", "2025-06-19", True,  "Direct",  0, "",   1450.00, "lista"),
        (11, 37, "2025-06-20", "2025-06-27", True,  "Booking", 1, "",   1085.00, "lista"),
        (0,  38, "2025-06-22", "2025-06-26", True,  "Airbnb",  0, "",    440.00, "lista"),
        (5,  39, "2025-06-25", "2025-06-29", True,  "Direct",  0, "",    600.00, "lista"),
        (7,  40, "2025-06-08", "2025-06-15", True,  "Booking", 0, "",   1610.00, "lista"),
        (1,  41, "2025-06-15", "2025-06-20", True,  "Airbnb",  0, "",   1400.00, "lista"),
        (9,  42, "2025-06-10", "2025-06-13", True,  "Direct",  0, "",    180.00, "lista"),
        # Juliol 2025
        (4,  43, "2025-07-05", "2025-07-12", True,  "Direct",  3, "Estiu alt",  4550.00, "lista"),
        (16, 44, "2025-07-05", "2025-07-12", True,  "Booking", 2, "",   3920.00, "lista"),
        (2,  45, "2025-07-05", "2025-07-12", True,  "Airbnb",  2, "",   3360.00, "lista"),
        (15, 46, "2025-07-05", "2025-07-12", True,  "Direct",  2, "",   3920.00, "lista"),
        (8,  47, "2025-07-12", "2025-07-19", True,  "Booking", 1, "",   2660.00, "lista"),
        (17, 48, "2025-07-05", "2025-07-12", True,  "Direct",  1, "",   2310.00, "lista"),
        (7,  49, "2025-07-12", "2025-07-19", True,  "Airbnb",  0, "",   1610.00, "lista"),
        (11, 20, "2025-07-19", "2025-07-26", True,  "Booking", 1, "",   1085.00, "lista"),
        (1,  21, "2025-07-14", "2025-07-19", True,  "Airbnb",  0, "",   1400.00, "lista"),
        (3,  22, "2025-07-20", "2025-07-25", True,  "Direct",  0, "",    475.00, "lista"),
        (0,  23, "2025-07-22", "2025-07-27", True,  "Booking", 0, "",    775.00, "lista"),
        (19, 24, "2025-07-12", "2025-07-19", True,  "Airbnb",  1, "",   1715.00, "lista"),
        # Agost 2025
        (4,  25, "2025-08-02", "2025-08-09", True,  "Direct",  3, "Agost alt",  4550.00, "lista"),
        (16, 26, "2025-08-02", "2025-08-09", True,  "Booking", 2, "",   3920.00, "lista"),
        (2,  27, "2025-08-02", "2025-08-09", True,  "Airbnb",  2, "",   3360.00, "lista"),
        (15, 28, "2025-08-09", "2025-08-16", True,  "Direct",  2, "",   3920.00, "lista"),
        (8,  29, "2025-08-09", "2025-08-16", True,  "Booking", 1, "",   2660.00, "lista"),
        (7,  30, "2025-08-16", "2025-08-23", True,  "Airbnb",  0, "",   1610.00, "lista"),
        (5,  31, "2025-08-10", "2025-08-15", True,  "Direct",  0, "",    975.00, "lista"),
        (0,  32, "2025-08-14", "2025-08-19", True,  "Booking", 0, "",    775.00, "lista"),
        (9,  33, "2025-08-05", "2025-08-09", True,  "Airbnb",  0, "",    340.00, "lista"),
        (17, 34, "2025-08-09", "2025-08-16", True,  "Direct",  1, "",   2310.00, "lista"),
        (19, 35, "2025-08-16", "2025-08-23", True,  "Airbnb",  1, "",   1715.00, "lista"),
        # Setembre 2025
        (2,  36, "2025-09-06", "2025-09-11", True,  "Direct",  1, "",   1550.00, "lista"),
        (16, 37, "2025-09-06", "2025-09-11", True,  "Booking", 1, "",   1750.00, "lista"),
        (0,  38, "2025-09-12", "2025-09-16", True,  "Airbnb",  0, "",    420.00, "lista"),
        (8,  39, "2025-09-12", "2025-09-17", True,  "Direct",  0, "",   1300.00, "lista"),
        (5,  40, "2025-09-15", "2025-09-19", True,  "Booking", 0, "",    560.00, "lista"),
        (11, 41, "2025-09-17", "2025-09-22", True,  "Airbnb",  0, "",    550.00, "lista"),
        (15, 42, "2025-09-13", "2025-09-18", True,  "Direct",  1, "",   1750.00, "lista"),
        (7,  43, "2025-09-20", "2025-09-24", False, "Booking", 0, "",    580.00, "cancelada"),
        (6,  44, "2025-09-22", "2025-09-26", True,  "Airbnb",  0, "",    320.00, "lista"),
        # Octubre 2025
        (5,  45, "2025-10-05", "2025-10-09", True,  "Direct",  0, "",    560.00, "lista"),
        (9,  46, "2025-10-10", "2025-10-14", True,  "Airbnb",  0, "",    240.00, "lista"),
        (14, 47, "2025-10-15", "2025-10-18", True,  "Booking", 0, "",    240.00, "lista"),
        (17, 48, "2025-10-08", "2025-10-12", True,  "Direct",  0, "",    880.00, "lista"),
        (0,  49, "2025-10-18", "2025-10-22", True,  "Airbnb",  0, "",    420.00, "lista"),
        # Novembre 2025
        (1,  20, "2025-11-07", "2025-11-10", True,  "Direct",  0, "",    630.00, "lista"),
        (6,  21, "2025-11-14", "2025-11-17", True,  "Booking", 0, "",    240.00, "lista"),
        (10, 22, "2025-11-20", "2025-11-23", True,  "Airbnb",  0, "",    315.00, "lista"),
        (14, 23, "2025-11-25", "2025-11-28", False, "Direct",  0, "",    240.00, "cancelada"),
        # Desembre 2025
        (0,  24, "2025-12-20", "2025-12-24", True,  "Direct",  0, "Nadal",     360.00, "lista"),
        (5,  25, "2025-12-22", "2025-12-27", True,  "Booking", 0, "Nadal",     600.00, "lista"),
        (2,  26, "2025-12-27", "2026-01-02", True,  "Airbnb",  1, "Cap d'any", 1620.00, "lista"),
        (1,  27, "2025-12-28", "2026-01-02", True,  "Direct",  0, "Cap d'any",  900.00, "lista"),

        # ── 2026 addicionals (31 reserves) ───────────────────────────────────
        # Gener 2026
        (5,  28, "2026-01-08", "2026-01-12", True,  "Direct",  0, "",    480.00, "lista"),
        (9,  29, "2026-01-18", "2026-01-22", True,  "Airbnb",  0, "",    240.00, "lista"),
        (16, 30, "2026-01-25", "2026-01-29", True,  "Booking", 0, "",   1200.00, "lista"),
        # Febrer 2026
        (2,  31, "2026-02-08", "2026-02-12", True,  "Direct",  1, "",   1080.00, "lista"),
        (6,  32, "2026-02-15", "2026-02-19", True,  "Booking", 0, "",    320.00, "lista"),
        (15, 33, "2026-02-20", "2026-02-24", True,  "Airbnb",  0, "",   1200.00, "lista"),
        # Marc 2026
        (2,  34, "2026-03-07", "2026-03-11", True,  "Airbnb",  0, "",   1080.00, "lista"),
        (7,  35, "2026-03-12", "2026-03-16", True,  "Direct",  0, "",    580.00, "lista"),
        (17, 36, "2026-03-18", "2026-03-22", True,  "Booking", 0, "",    800.00, "lista"),
        # Abril 2026 - Setmana Santa
        (2,  37, "2026-04-04", "2026-04-11", True,  "Direct",  1, "Setmana Santa",  2380.00, "lista"),
        (4,  38, "2026-04-04", "2026-04-11", True,  "Airbnb",  2, "Setmana Santa",  3640.00, "lista"),
        (16, 39, "2026-04-04", "2026-04-09", True,  "Booking", 1, "Setmana Santa",  2250.00, "lista"),
        # Maig 2026
        (4,  40, "2026-05-09", "2026-05-14", False, "Direct",  1, "",   2100.00, "lista"),
        (8,  41, "2026-05-08", "2026-05-12", True,  "Booking", 0, "",   1160.00, "lista"),
        (16, 42, "2026-05-15", "2026-05-20", True,  "Airbnb",  0, "",   1900.00, "lista"),
        # Juny 2026 (futur proper)
        (4,  43, "2026-06-06", "2026-06-13", False, "Direct",  2, "",   2940.00, "reservada"),
        (16, 44, "2026-06-06", "2026-06-13", False, "Booking", 1, "",   2660.00, "reservada"),
        (2,  45, "2026-06-13", "2026-06-20", False, "Airbnb",  1, "",   2380.00, "reservada"),
        (8,  46, "2026-06-20", "2026-06-25", False, "Direct",  0, "",   1450.00, "reservada"),
        # Juliol 2026 (futur)
        (4,  47, "2026-07-04", "2026-07-11", False, "Direct",  3, "",   4550.00, "prereservada"),
        (16, 48, "2026-07-04", "2026-07-11", False, "Booking", 2, "",   3920.00, "prereservada"),
        (2,  49, "2026-07-04", "2026-07-11", False, "Airbnb",  2, "",   3360.00, "prereservada"),
        # Agost 2026 (futur)
        (4,  20, "2026-08-01", "2026-08-08", False, "Direct",  3, "",   4550.00, "prereservada"),
        (15, 21, "2026-08-01", "2026-08-08", False, "Booking", 2, "",   3920.00, "prereservada"),
        # Octubre 2026 (futur)
        (0,  22, "2026-10-05", "2026-10-09", False, "Direct",  0, "",    420.00, "prereservada"),
        (5,  23, "2026-10-12", "2026-10-16", False, "Booking", 0, "",    560.00, "prereservada"),
        (9,  24, "2026-10-18", "2026-10-21", False, "Airbnb",  0, "",    180.00, "prereservada"),
        # Novembre 2026 (futur)
        (1,  25, "2026-11-07", "2026-11-10", False, "Direct",  0, "",    630.00, "prereservada"),
        (6,  26, "2026-11-14", "2026-11-17", False, "Booking", 0, "",    240.00, "prereservada"),
        # Desembre 2026 (futur)
        (17, 27, "2026-12-20", "2026-12-24", False, "Airbnb",  0, "Nadal",     800.00, "prereservada"),
        (2,  28, "2026-12-26", "2027-01-02", False, "Direct",  1, "Cap d'any", 1890.00, "prereservada"),
    ]

    metodes_cicle = ["transferencia", "targeta", "bizum", "efectiu", "targeta", "transferencia", "bizum"]

    reserves = []
    for row in reserves_data:
        imm_i, inq_i, entrada, sortida, pagat, tipus, lim, coment, import_total, estat_reserva = row
        estat_pag = 'pagada' if pagat else ('rebutjada' if estat_reserva == 'cancelada' else 'pendent')
        r = ReservaBasica.objects.create(
            immoble=immobles[imm_i],
            inquili=tots_inquilins[inq_i],
            data_entrada=entrada,
            data_sortida=sortida,
            pagat=pagat,
            tipus_reserva=tipus,
            limpieza_extra=lim,
            comentaris_interns=coment,
            import_total=import_total,
            import_pagat=import_total if pagat else 0,
            import_pendent=0 if pagat else import_total,
            estat_reserva=estat_reserva,
            estat_pagament=estat_pag,
        )
        reserves.append(r)

    print(f"{len(reserves)} reserves creades")

    # ── Hostes (~2-3 per reserva) ─────────────────────────────────────────────
    hostes_extra = [
        ("Aina Puig Coma",    "Dona",  "Parella",       "DNI",       "11112222Z", "Espanyola",  "1995-03-12", "Carrer Major 5, Barcelona",       "aina.puig@gmail.com",   "+34 600 000 001"),
        ("Eric Bosch Pons",   "Home",  "Fill/a",        "DNI",       "22223333Y", "Espanyola",  "2015-07-22", "Carrer Major 5, Barcelona",       "",                      ""),
        ("Maria Solans Roca", "Dona",  "Fill/a",        "DNI",       "33334444X", "Espanyola",  "2018-11-04", "Avinguda Diagonal 10, Barcelona", "",                      ""),
        ("Pau Llopis Vila",   "Home",  "Parella",       "Passaport", "AB1234567", "Francesa",   "1988-01-30", "Rue de la Paix 12, Paris",        "pau.llopis@gmail.com",  "+33 6 12 34 56 78"),
        ("Clara Ferrer Mas",  "Dona",  "Germa/Germana", "DNI",       "44445555W", "Espanyola",  "1993-06-18", "Placa Catalunya 8, Tarragona",    "clara.ferrer@gmail.com","+34 600 000 002"),
        ("Roger Pla Font",    "Home",  "Fill/a",        "DNI",       "55556666V", "Espanyola",  "2012-04-09", "Carrer del Pi 12, Lleida",        "",                      ""),
        ("Laia Vidal Mas",    "Dona",  "Parella",       "NIE",       "Y1234567B", "Argentina",  "1991-09-25", "Rambla Nova 20, Tarragona",       "laia.vidal@gmail.com",  "+54 11 1234 5678"),
        ("Marti Coll Vives",  "Home",  "Fill/a",        "DNI",       "66667777U", "Espanyola",  "2019-02-14", "Carrer Balmes 55, Barcelona",     "",                      ""),
        ("Berta Sole Pons",   "Dona",  "Parella",       "DNI",       "77778888T", "Espanyola",  "1986-12-01", "Via Augusta 3, Barcelona",        "berta.sole@gmail.com",  "+34 600 000 003"),
        ("Nil Camps Ros",     "Home",  "Parella",       "DNI",       "88889999S", "Espanyola",  "1990-08-15", "Carrer Groc 7, Reus",             "nil.camps@gmail.com",   "+34 600 000 004"),
        ("Quim Sala Mas",     "Home",  "Fill/a",        "DNI",       "99990000R", "Espanyola",  "2014-05-20", "Passeig de la Pau 1, Vic",        "",                      ""),
        ("Mireia Roca Pla",   "Dona",  "Parella",       "DNI",       "00001111Q", "Espanyola",  "1992-10-03", "Carrer dels Albers 4, Manresa",   "mireia.roca@gmail.com", "+34 600 000 005"),
    ]

    total_hostes = 0
    for idx, reserva in enumerate(reserves):
        inq = reserva.inquili
        Hoste.objects.create(
            reserva=reserva, es_principal=True,
            nom_complet=inq.nom_complet,
            genere="Home" if idx % 2 == 0 else "Dona",
            tipus_document="DNI",
            numero_document=inq.dni_passaport,
            nacionalitat="Espanyola",
            data_naixement=f"19{70 + (idx % 30):02d}-0{1 + (idx % 9)}-15",
            residencia=inq.residencia,
            email=inq.email,
            telefon=f"+34 6{idx % 100:02d} {idx % 1000:03d} {idx % 100:03d}",
        )
        total_hostes += 1

        # 0, 1 o 2 hostes addicionals segons import (grans reserves = mes gent)
        import_total_val = float(reserves_data[idx][8])
        num_extra = 0 if import_total_val < 400 else (1 if import_total_val < 1500 else 2)
        for e in range(num_extra):
            extra = hostes_extra[(idx + e) % len(hostes_extra)]
            nom, gen, rel, dtype, dnum, nac, naix, res, em, tel = extra
            Hoste.objects.create(
                reserva=reserva, es_principal=False,
                nom_complet=nom, genere=gen, relacio_parental=rel,
                tipus_document=dtype, numero_document=dnum,
                nacionalitat=nac, data_naixement=naix,
                residencia=res, email=em, telefon=tel,
            )
            total_hostes += 1

        reserva.num_hostes = reserva.hostes.count()
        reserva.save(update_fields=['num_hostes'])

    print(f"{total_hostes} hostes creats")

    # ── Pagaments (bulk_create per evitar signals d'email) ───────────────────
    from django.db.models.signals import post_save
    from bookings import signals as booking_signals
    post_save.disconnect(booking_signals.pagament_post_save, sender=PagamentReserva)

    pagaments_bulk = []
    for idx, (reserva, row) in enumerate(zip(reserves, reserves_data)):
        imm_i, inq_i, entrada, sortida, pagat, tipus, lim, coment, import_total, estat_reserva = row
        metode = metodes_cicle[idx % len(metodes_cicle)]
        data_entrada_dt = date.fromisoformat(entrada)
        data_pag = str(data_entrada_dt - timedelta(days=3))

        if estat_reserva == 'cancelada':
            pagaments_bulk.append(PagamentReserva(
                reserva=reserva, data_pagament=data_pag,
                import_pagament=import_total, metode_pagament=metode, estat='cancelat',
            ))
        elif pagat:
            if import_total >= 2000:
                meitat = round(import_total / 2, 2)
                data_pag2 = str(data_entrada_dt - timedelta(days=30))
                pagaments_bulk.append(PagamentReserva(
                    reserva=reserva, data_pagament=data_pag2,
                    import_pagament=meitat, metode_pagament=metode, estat='pagat',
                ))
                pagaments_bulk.append(PagamentReserva(
                    reserva=reserva, data_pagament=data_pag,
                    import_pagament=import_total - meitat, metode_pagament=metode, estat='pagat',
                ))
            else:
                pagaments_bulk.append(PagamentReserva(
                    reserva=reserva, data_pagament=data_pag,
                    import_pagament=import_total, metode_pagament=metode, estat='pagat',
                ))
        else:
            pagaments_bulk.append(PagamentReserva(
                reserva=reserva, data_pagament=data_pag,
                import_pagament=import_total, metode_pagament=metode, estat='pendent',
            ))

    PagamentReserva.objects.bulk_create(pagaments_bulk)
    post_save.connect(booking_signals.pagament_post_save, sender=PagamentReserva)
    print(f"{len(pagaments_bulk)} pagaments creats")
    print("Tot OK!")


if __name__ == "__main__":
    run()
