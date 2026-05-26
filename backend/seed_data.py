"""
Seed script: crea un usuari admin, 20 immobles, 20 inquilins i 20 reserves.
Executa'l des de la carpeta backend/:

python seed_data.py

AVÍS: esborra tots els registres existents de reserves, inquilins i immobles
abans de crear-ne de nous. L'usuari admin NO s'esborra si ja existeix.

REQUISIT PREVI, EXECUTAR A LA CARPETA DE BACKEND: python manage.py migrate

Credencials de l'usuari creat:
    NIP:      ADM001
    Password: DomusGestor2026!
"""



import os
import sys

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
    # Columnes: nom, ref, adreca, ciutat, cp, tipus, capacitat, hab, banys,
    #           m2, preu_nit, actiu,
    #           propietari_nom, propietari_dni, propietari_email,
    #           propietari_telefon, propietari_adreca, propietari_iban
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

    # Fotos de placeholder per immoble (3-5 URLs per immoble).
    # La primera URL de cada llista és la foto de portada.
    # En producció aquestes URLs apuntaran al servidor d'emmagatzematge (veure README).
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

    # Horaris de check-in / check-out per immoble (mateixa ordre que immobles_data).
    # Format: (hora_checkin_inici, hora_checkin_fi, hora_checkout_inici, hora_checkout_fi)
    horaris_per_immoble = [
        # 0 · Apartament Gracia Centre — pis urbà Barcelona
        ("15:00", "21:00", "07:00", "11:00"),
        # 1 · Atic Vista Mar — àtic Barcelona
        ("16:00", "21:00", "08:00", "11:00"),
        # 2 · Casa amb jardi Sitges — casa costa
        ("16:00", "20:00", "09:00", "12:00"),
        # 3 · Estudi Barceloneta — estudi urbà costa
        ("15:00", "22:00", "07:00", "11:00"),
        # 4 · Xalet Costa Brava — xalet gran costa
        ("17:00", "21:00", "09:00", "12:00"),
        # 5 · Pis Modern Eixample — pis urbà Barcelona
        ("15:00", "21:00", "08:00", "11:00"),
        # 6 · Apartament Girona Vella — pis urbà Girona
        ("15:00", "20:00", "08:00", "11:00"),
        # 7 · Duplex Tarragona Mar — dúplex costa
        ("16:00", "21:00", "09:00", "12:00"),
        # 8 · Casa Rural Osona — casa rural
        ("17:00", "20:00", "09:00", "12:00"),
        # 9 · Apartament Lleida Centre — pis urbà Lleida
        ("14:00", "20:00", "08:00", "11:00"),
        # 10 · Atic Terrassa Vista — àtic urbà
        ("15:00", "21:00", "08:00", "11:00"),
        # 11 · Pis Badalona Platja — pis costa urbana
        ("16:00", "21:00", "08:00", "11:00"),
        # 12 · Casa Adossada Sabadell — casa (inactiva)
        ("15:00", "20:00", "08:00", "11:00"),
        # 13 · Estudi Mataro Rambla — estudi costa
        ("15:00", "21:00", "07:00", "11:00"),
        # 14 · Apartament Manresa Nou — pis urbà
        ("14:00", "20:00", "08:00", "11:00"),
        # 15 · Xalet Roses Costa — xalet gran costa
        ("17:00", "21:00", "09:00", "12:00"),
        # 16 · Pis Figueres Rambla — pis urbà
        ("15:00", "20:00", "08:00", "11:00"),
        # 17 · Casa Rural Priorat — casa rural
        ("17:00", "20:00", "09:00", "12:00"),
        # 18 · Apartament Tortosa Riu — pis urbà (check-in autònom)
        ("15:00", "23:00", "07:00", "11:00"),
        # 19 · Duplex Vilanova Centre — dúplex costa
        ("16:00", "21:00", "08:00", "12:00"),
    ]

    immobles = []
    for row, fotos, horaris in zip(immobles_data, fotos_per_immoble, horaris_per_immoble):
        (nom, ref, adr, ciutat, cp, tipus, cap, hab, banys, m2, preu, actiu,
         prop_nom, prop_dni, prop_email, prop_tel, prop_adr, prop_iban) = row
        ci_inici, ci_fi, co_inici, co_fi = horaris
        propietari = Persona.objects.create(
            nom_complet=prop_nom,
            dni_passaport=prop_dni,
            email=prop_email,
            telefon=prop_tel,
            residencia=prop_adr,
        )
        PerfilPropietari.objects.create(
            persona=propietari,
            iban=prop_iban,
            adreca_facturacio=prop_adr,
        )
        imm = Immoble.objects.create(
            nom_comercial=nom, referencia=ref, adreca=adr, ciutat=ciutat,
            codi_postal=cp, tipus_immoble=tipus, capacitat_maxima=cap,
            num_habitacions=hab, num_banys=banys, metres_quadrats=m2,
            preu_base_nit=preu, actiu=actiu,
            propietari=propietari,
            fotos=fotos,
            hora_checkin_inici=ci_inici,
            hora_checkin_fi=ci_fi,
            hora_checkout_inici=co_inici,
            hora_checkout_fi=co_fi,
        )
        immobles.append(imm)

    print(f"{len(immobles)} immobles creats")

    # ── Serveis ──────────────────────────────────────────────────────────────
    # (nom, icona, categoria)
    serveis_data = [
        # Climatització
        ("Aire acondicionat",        "AirVent",       "climatitzacio"),
        ("Calefacció",               "Flame",          "climatitzacio"),
        ("Ventilador de sostre",     "Fan",            "climatitzacio"),
        # Connectivitat
        ("WiFi",                     "Wifi",           "conectivitat"),
        ("TV pantalla plana",        "Tv",             "conectivitat"),
        ("Netflix",                  "MonitorPlay",    "conectivitat"),
        # Electrodomèstics
        ("Rentadora",                "WashingMachine", "electrodomestics"),
        ("Assecadora",               "Wind",           "electrodomestics"),
        ("Rentavaixelles",           "Sparkles",       "electrodomestics"),
        ("Cuina totalment equipada", "ChefHat",        "electrodomestics"),
        ("Microones",                "Microwave",      "electrodomestics"),
        ("Cafetera",                 "Coffee",         "electrodomestics"),
        ("Planxa i taula de planxar","Shirt",          "electrodomestics"),
        # Exterior
        ("Piscina",                  "Waves",          "exterior"),
        ("Jardí privat",             "TreePine",       "exterior"),
        ("Terrassa",                 "Armchair",       "exterior"),
        ("Barbacoa",                 "Drumstick",      "exterior"),
        ("Aparcament gratuït",       "Car",            "exterior"),
        ("Garatge privat",           "Warehouse",      "exterior"),
        # Altres
        ("Ascensor",                 "ArrowUpDown",    "altres"),
        ("Caixa forta",              "Lock",           "altres"),
        ("Admeten mascotes",         "Dog",            "altres"),
        ("Accés adaptat",            "Accessibility",  "altres"),
        ("Llençols inclosos",        "Bed",            "altres"),
        ("Tovalloles incloses",      "Bath",           "altres"),
        ("Bressol disponible",       "Baby",           "altres"),
        ("Check-in autònom",         "Key",            "altres"),
    ]

    serveis_obj = {}
    for nom, icona, categoria in serveis_data:
        s = Servei.objects.create(nom=nom, icona=icona, categoria=categoria)
        serveis_obj[nom] = s

    print(f"{len(serveis_obj)} serveis creats")

    # ── Assignació de serveis per immoble ────────────────────────────────────
    # Cada llista conté els noms dels serveis que té l'immoble (per índex).
    assignacions = [
        # 0 · Apartament Gracia Centre — Pis Barcelona, 85m², 4 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Rentadora",
         "TV pantalla plana", "Cuina totalment equipada", "Ascensor",
         "Llençols inclosos", "Tovalloles incloses"],

        # 1 · Atic Vista Mar — Àtic Barcelona, 65m², 2 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Terrassa",
         "TV pantalla plana", "Netflix", "Cuina totalment equipada",
         "Rentadora", "Ascensor", "Llençols inclosos"],

        # 2 · Casa amb jardi Sitges — Casa, 200m², 8 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Piscina", "Jardí privat",
         "Barbacoa", "Rentadora", "Assecadora", "Rentavaixelles",
         "TV pantalla plana", "Cuina totalment equipada", "Aparcament gratuït",
         "Admeten mascotes", "Llençols inclosos", "Tovalloles incloses"],

        # 3 · Estudi Barceloneta — Estudi, 28m², 2 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "TV pantalla plana",
         "Cuina totalment equipada", "Microones", "Cafetera", "Ascensor"],

        # 4 · Xalet Costa Brava — Xalet, 320m², 10 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Piscina", "Jardí privat",
         "Barbacoa", "Terrassa", "Rentadora", "Assecadora", "Rentavaixelles",
         "Cuina totalment equipada", "TV pantalla plana", "Netflix",
         "Aparcament gratuït", "Garatge privat", "Admeten mascotes",
         "Bressol disponible", "Caixa forta"],

        # 5 · Pis Modern Eixample — Pis, 90m², 4 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Rentadora", "Rentavaixelles",
         "TV pantalla plana", "Netflix", "Cuina totalment equipada",
         "Planxa i taula de planxar", "Ascensor", "Llençols inclosos",
         "Tovalloles incloses", "Cafetera"],

        # 6 · Apartament Girona Vella — Pis, 75m², 3 persones
        ["WiFi", "Calefacció", "TV pantalla plana", "Cuina totalment equipada",
         "Rentadora", "Ascensor", "Llençols inclosos", "Microones"],

        # 7 · Duplex Tarragona Mar — Dúplex, 120m², 5 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Terrassa",
         "TV pantalla plana", "Rentadora", "Cuina totalment equipada",
         "Aparcament gratuït", "Llençols inclosos", "Admeten mascotes",
         "Barbacoa"],

        # 8 · Casa Rural Osona — Casa Rural, 350m², 12 persones
        ["WiFi", "Calefacció", "Piscina", "Jardí privat", "Barbacoa",
         "Rentadora", "Assecadora", "Cuina totalment equipada", "TV pantalla plana",
         "Aparcament gratuït", "Admeten mascotes", "Bressol disponible",
         "Check-in autònom", "Ventilador de sostre"],

        # 9 · Apartament Lleida Centre — Pis, 80m², 4 persones
        ["WiFi", "Calefacció", "TV pantalla plana", "Cuina totalment equipada",
         "Rentadora", "Ascensor", "Microones", "Cafetera"],

        # 10 · Atic Terrassa Vista — Àtic, 95m², 3 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Terrassa",
         "TV pantalla plana", "Netflix", "Rentadora", "Cuina totalment equipada",
         "Ascensor", "Planxa i taula de planxar"],

        # 11 · Pis Badalona Platja — Pis, 100m², 5 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Terrassa",
         "TV pantalla plana", "Rentadora", "Rentavaixelles",
         "Cuina totalment equipada", "Aparcament gratuït", "Llençols inclosos",
         "Tovalloles incloses"],

        # 12 · Casa Adossada Sabadell — Casa (inactiva), 150m², 6 persones
        ["WiFi", "Calefacció", "Jardí privat", "TV pantalla plana",
         "Rentadora", "Cuina totalment equipada", "Garatge privat",
         "Admeten mascotes"],

        # 13 · Estudi Mataro Rambla — Estudi, 40m², 2 persones
        ["WiFi", "Aire acondicionat", "TV pantalla plana",
         "Cuina totalment equipada", "Microones", "Cafetera", "Ascensor"],

        # 14 · Apartament Manresa Nou — Pis, 70m², 3 persones
        ["WiFi", "Calefacció", "TV pantalla plana", "Rentadora",
         "Cuina totalment equipada", "Ascensor", "Llençols inclosos",
         "Planxa i taula de planxar"],

        # 15 · Xalet Roses Costa — Xalet, 240m², 8 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Piscina", "Jardí privat",
         "Barbacoa", "Terrassa", "Rentadora", "Assecadora",
         "Cuina totalment equipada", "TV pantalla plana", "Netflix",
         "Aparcament gratuït", "Admeten mascotes", "Caixa forta",
         "Llençols inclosos", "Tovalloles incloses"],

        # 16 · Pis Figueres Rambla — Pis, 85m², 4 persones
        ["WiFi", "Calefacció", "TV pantalla plana", "Rentadora",
         "Cuina totalment equipada", "Ascensor", "Planxa i taula de planxar",
         "Microones"],

        # 17 · Casa Rural Priorat — Casa Rural, 280m², 10 persones
        ["WiFi", "Calefacció", "Jardí privat", "Barbacoa", "Rentadora",
         "Assecadora", "Cuina totalment equipada", "TV pantalla plana",
         "Aparcament gratuït", "Admeten mascotes", "Bressol disponible",
         "Ventilador de sostre"],

        # 18 · Apartament Tortosa Riu — Pis, 80m², 4 persones
        ["WiFi", "Calefacció", "TV pantalla plana", "Cuina totalment equipada",
         "Rentadora", "Ascensor", "Check-in autònom", "Microones"],

        # 19 · Duplex Vilanova Centre — Dúplex, 140m², 6 persones
        ["WiFi", "Aire acondicionat", "Calefacció", "Terrassa",
         "TV pantalla plana", "Netflix", "Rentadora", "Rentavaixelles",
         "Cuina totalment equipada", "Aparcament gratuït", "Llençols inclosos",
         "Tovalloles incloses"],
    ]

    for imm, noms_serveis in zip(immobles, assignacions):
        imm.serveis.set([serveis_obj[nom] for nom in noms_serveis])

    print("Serveis assignats als immobles")

    # ── Temporades ───────────────────────────────────────────────────────────
    # Format: (immoble_idx, nom, data_inici, data_fi, preu_nit, min_nits, dies_checkin)
    # dies_checkin: [] = qualsevol dia, [5] = dissabte, [5,6] = dissabte+diumenge, etc.
    # 0=Dl 1=Dt 2=Dc 3=Dj 4=Dv 5=Ds 6=Dg
    # ── Temporades ───────────────────────────────────────────────────────────
    # Format: (immoble_idx, nom, data_inici, data_fi, preu_nit, min_nits, dies_checkin, comissio)
    # dies_checkin: [] = qualsevol dia, [5] = dissabte, [5,6] = dissabte+diumenge, etc.
    # 0=Dl 1=Dt 2=Dc 3=Dj 4=Dv 5=Ds 6=Dg
    temporades_data = [
        # 0 · Apartament Gracia Centre (base 110 €) — urbà Barcelona
        (0, "Temporada Baixa",      "2000-01-01", "2000-03-31",  90.00, 2, [], 10.00),
        (0, "Temporada Mitja",      "2000-04-01", "2000-06-30", 110.00, 3, [], 15.00),
        (0, "Temporada Alta",       "2000-07-01", "2000-08-31", 155.00, 3, [], 20.00),
        (0, "Temporada Mitja Tard", "2000-09-01", "2000-12-31", 105.00, 2, [], 15.00),

        # 1 · Atic Vista Mar (base 220 €) — urbà Barcelona
        (1, "Temporada Baixa",      "2000-01-01", "2000-05-31", 180.00, 2, [], 15.00),
        (1, "Temporada Alta",       "2000-06-01", "2000-09-15", 280.00, 3, [], 20.00),
        (1, "Temporada Mitja",      "2000-09-16", "2000-12-31", 210.00, 2, [], 15.00),

        # 2 · Casa amb jardi Sitges (base 350 €) — costa
        (2, "Hivern",               "2000-01-01", "2000-03-31", 270.00, 2, [], 10.00),
        (2, "Primavera",            "2000-04-01", "2000-06-30", 340.00, 3, [], 15.00),
        (2, "Estiu",                "2000-07-01", "2000-08-31", 480.00, 7, [5, 6], 20.00),
        (2, "Tardor",               "2000-09-01", "2000-12-31", 310.00, 3, [], 10.00),

        # 3 · Estudi Barceloneta (base 75 €) — urbà costa
        (3, "Temporada Baixa",      "2000-01-01", "2000-06-14",  65.00, 2, [], 10.00),
        (3, "Temporada Alta",       "2000-06-15", "2000-09-15",  95.00, 3, [], 15.00),
        (3, "Temporada Baixa",      "2000-09-16", "2000-12-31",  65.00, 2, [], 10.00),

        # 4 · Xalet Costa Brava (base 480 €) — costa gran
        (4, "Temporada Baixa",      "2000-01-01", "2000-03-31", 360.00, 2, [], 10.00),
        (4, "Setmana Santa",        "2000-04-01", "2000-04-12", 520.00, 5, [5, 6], 20.00),
        (4, "Primavera/Tardor",     "2000-04-13", "2000-06-30", 420.00, 3, [], 15.00),
        (4, "Temporada Alta",       "2000-07-01", "2000-08-31", 650.00, 7, [5, 6], 20.00),
        (4, "Tardor/Hivern",        "2000-09-01", "2000-12-31", 400.00, 3, [], 15.00),

        # 5 · Pis Modern Eixample (base 150 €) — urbà Barcelona
        (5, "Temporada Baixa",      "2000-01-01", "2000-03-31", 120.00, 2, [], 10.00),
        (5, "Temporada Mitja",      "2000-04-01", "2000-06-30", 150.00, 3, [], 15.00),
        (5, "Temporada Alta",       "2000-07-01", "2000-08-31", 195.00, 3, [], 18.00),
        (5, "Temporada Mitja Tard", "2000-09-01", "2000-12-31", 140.00, 2, [], 15.00),

        # 6 · Apartament Girona Vella (base 95 €) — urbà
        (6, "Hivern",               "2000-01-01", "2000-05-31",  80.00, 2, [], 10.00),
        (6, "Estiu",                "2000-06-01", "2000-09-30", 115.00, 3, [], 18.00),
        (6, "Tardor/Hivern",        "2000-10-01", "2000-12-31",  80.00, 2, [], 10.00),

        # 7 · Duplex Tarragona Mar (base 180 €) — costa
        (7, "Temporada Baixa",      "2000-01-01", "2000-05-31", 145.00, 2, [], 12.00),
        (7, "Temporada Alta",       "2000-06-01", "2000-09-15", 230.00, 7, [5, 6], 18.00),
        (7, "Temporada Baixa",      "2000-09-16", "2000-12-31", 145.00, 2, [], 12.00),

        # 8 · Casa Rural Osona (base 300 €) — rural
        (8, "Hivern",               "2000-01-01", "2000-03-31", 240.00, 2, [], 15.00),
        (8, "Primavera",            "2000-04-01", "2000-06-30", 290.00, 3, [5], 15.00),
        (8, "Estiu",                "2000-07-01", "2000-08-31", 380.00, 7, [5, 6], 20.00),
        (8, "Tardor",               "2000-09-01", "2000-12-31", 260.00, 3, [], 15.00),

        # 9 · Apartament Lleida Centre (base 70 €) — urbà
        (9, "Temporada Baixa",      "2000-01-01", "2000-06-30",  60.00, 2, [], 10.00),
        (9, "Temporada Alta",       "2000-07-01", "2000-08-31",  85.00, 3, [], 15.00),
        (9, "Temporada Baixa",      "2000-09-01", "2000-12-31",  60.00, 2, [], 10.00),

        # 10 · Atic Terrassa Vista (base 130 €) — urbà
        (10, "Temporada Baixa",     "2000-01-01", "2000-05-31", 105.00, 2, [], 12.00),
        (10, "Temporada Alta",      "2000-06-01", "2000-09-15", 165.00, 3, [], 18.00),
        (10, "Temporada Baixa",     "2000-09-16", "2000-12-31", 105.00, 2, [], 12.00),

        # 11 · Pis Badalona Platja (base 120 €) — costa urbana
        (11, "Temporada Baixa",     "2000-01-01", "2000-05-31",  95.00, 2, [], 10.00),
        (11, "Temporada Alta",      "2000-06-01", "2000-09-15", 155.00, 7, [5, 6], 20.00),
        (11, "Temporada Mitja",     "2000-09-16", "2000-12-31", 110.00, 3, [], 15.00),

        # 12 · Casa Adossada Sabadell — inactiva (base 160 €)
        (12, "Temporada Baixa",     "2000-01-01", "2000-06-30", 130.00, 2, [], 10.00),
        (12, "Temporada Alta",      "2000-07-01", "2000-08-31", 190.00, 3, [], 15.00),
        (12, "Temporada Baixa",     "2000-09-01", "2000-12-31", 130.00, 2, [], 10.00),

        # 13 · Estudi Mataro Rambla (base 65 €) — costa
        (13, "Temporada Baixa",     "2000-01-01", "2000-06-14",  55.00, 2, [], 10.00),
        (13, "Temporada Alta",      "2000-06-15", "2000-09-15",  80.00, 7, [5, 6], 15.00),
        (13, "Temporada Baixa",     "2000-09-16", "2000-12-31",  55.00, 2, [], 10.00),

        # 14 · Apartament Manresa Nou (base 80 €) — urbà
        (14, "Temporada Única",     "2000-01-01", "2000-12-31",  80.00, 2, [], 10.00),

        # 15 · Xalet Roses Costa (base 400 €) — costa gran
        (15, "Hivern",              "2000-01-01", "2000-03-31", 300.00, 2, [], 15.00),
        (15, "Setmana Santa",       "2000-04-01", "2000-04-12", 450.00, 5, [5, 6], 20.00),
        (15, "Primavera",           "2000-04-13", "2000-06-30", 380.00, 3, [], 15.00),
        (15, "Temporada Alta",      "2000-07-01", "2000-08-31", 560.00, 7, [5, 6], 20.00),
        (15, "Tardor/Hivern",       "2000-09-01", "2000-12-31", 350.00, 3, [], 15.00),

        # 16 · Pis Figueres Rambla (base 85 €) — urbà
        (16, "Temporada Baixa",     "2000-01-01", "2000-06-30",  70.00, 2, [], 10.00),
        (16, "Temporada Alta",      "2000-07-01", "2000-08-31", 105.00, 3, [], 15.00),
        (16, "Temporada Baixa",     "2000-09-01", "2000-12-31",  70.00, 2, [], 10.00),

        # 17 · Casa Rural Priorat (base 260 €) — rural
        (17, "Hivern",              "2000-01-01", "2000-03-31", 200.00, 2, [], 15.00),
        (17, "Primavera/Tardor",    "2000-04-01", "2000-06-30", 250.00, 3, [5], 15.00),
        (17, "Estiu",               "2000-07-01", "2000-08-31", 330.00, 7, [5, 6], 20.00),
        (17, "Tardor",              "2000-09-01", "2000-12-31", 220.00, 3, [], 15.00),

        # 18 · Apartament Tortosa Riu (base 75 €) — urbà
        (18, "Temporada Baixa",     "2000-01-01", "2000-06-30",  65.00, 2, [], 10.00),
        (18, "Temporada Alta",      "2000-07-01", "2000-08-31",  90.00, 3, [], 15.00),
        (18, "Temporada Baixa",     "2000-09-01", "2000-12-31",  65.00, 2, [], 10.00),

        # 19 · Duplex Vilanova Centre (base 195 €) — costa
        (19, "Temporada Baixa",     "2000-01-01", "2000-05-31", 155.00, 2, [], 15.00),
        (19, "Temporada Alta",      "2000-06-01", "2000-09-15", 245.00, 7, [5, 6], 20.00),
        (19, "Temporada Mitja",     "2000-09-16", "2000-12-31", 180.00, 3, [], 15.00),
    ]

    temporades = [
        Temporada.objects.create(
            immoble=immobles[idx],
            nom=nom,
            data_inici=inici,
            data_fi=fi,
            preu_nit=preu,
            min_nits=min_nits,
            dies_checkin=dies_checkin,
            comissio=comissio, # <-- AFEGIT AQUÍ
        )
        for idx, nom, inici, fi, preu, min_nits, dies_checkin, comissio in temporades_data # <-- AFEGIT AQUÍ
    ]
    print(f"{len(temporades)} temporades creades")

    # ── 20 Inquilins ─────────────────────────────────────────────────────────
    # DNIs ficticis (no coincideixen amb els propietaris per evitar colisions)
    inquilins_data = [
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
    ]

    inquilins = []
    for nom, dni, email, residencia in inquilins_data:
        inq = Persona.objects.create(
            nom_complet=nom,
            dni_passaport=dni,
            email=email,
            residencia=residencia,
        )
        PerfilInquili.objects.create(persona=inq)
        inquilins.append(inq)

    print(f"{len(inquilins)} inquilins (Persona+PerfilInquili) creats")

    # ── 20 Reserves ──────────────────────────────────────────────────────────
    # (immoble_idx, inquili_idx, data_entrada, data_sortida, pagat,
    #  tipus_reserva, limpieza_extra, comentaris)
    reserves_data = [
        (0,  0,  "2026-01-10", "2026-01-15", True,  "Airbnb",  1, "Entrada abans de les 15:00 si es possible."),
        (1,  1,  "2026-01-20", "2026-01-23", True,  "Booking", 0, "Hostes habituals, llits separats."),
        (2,  2,  "2026-02-03", "2026-02-10", True,  "Direct",  2, "Reserva familiar, necessiten bressol."),
        (3,  3,  "2026-02-14", "2026-02-16", False, "Airbnb",  0, "Sant Valenti - decoracio especial."),
        (4,  4,  "2026-03-01", "2026-03-08", True,  "Direct",  3, "Estada llarga, descompte aplicat."),
        (5,  5,  "2026-03-15", "2026-03-18", False, "Booking", 0, ""),
        (6,  6,  "2026-04-05", "2026-04-07", True,  "Airbnb",  1, "Cap d'any avancat - Setmana Santa."),
        (7,  7,  "2026-04-20", "2026-04-25", False, "Direct",  0, "Pendent confirmacio pagament."),
        (8,  8,  "2026-05-01", "2026-05-05", True,  "Booking", 2, "Festa local, possible soroll."),
        (9,  9,  "2026-05-10", "2026-05-17", False, "Airbnb",  0, ""),
        (10, 10, "2026-05-20", "2026-05-22", True,  "Direct",  1, "Treball, necessita wifi rapid."),
        (11, 11, "2026-06-01", "2026-06-08", False, "Booking", 0, ""),
        (12, 12, "2026-06-15", "2026-06-20", True,  "Airbnb",  2, "Aniversari de noces."),
        (13, 13, "2026-07-01", "2026-07-07", False, "Altres",  0, "Reserva via partner extern."),
        (14, 14, "2026-07-10", "2026-07-14", True,  "Direct",  1, ""),
        (15, 15, "2026-07-20", "2026-07-25", False, "Booking", 2, "Mascota petita autoritzada."),
        (16, 16, "2026-08-01", "2026-08-10", True,  "Airbnb",  3, "Vacances familiars d'estiu."),
        (17, 17, "2026-08-15", "2026-08-18", True,  "Direct",  0, "Pagat per transferencia."),
        (18, 18, "2026-09-01", "2026-09-05", False, "Booking", 1, ""),
        (19, 19, "2026-09-10", "2026-09-15", True,  "Airbnb",  2, "Check-in autonom amb codi."),
    ]

    reserves = []
    for row in reserves_data:
        imm_i, inq_i, entrada, sortida, pagat, tipus, limpieza_extra, comentaris = row
        r = ReservaBasica.objects.create(
            immoble=immobles[imm_i],
            inquili=inquilins[inq_i],
            data_entrada=entrada,
            data_sortida=sortida,
            pagat=pagat,
            tipus_reserva=tipus,
            limpieza_extra=limpieza_extra,
            comentaris_interns=comentaris,
        )
        reserves.append(r)

    print(f"{len(reserves)} reserves creades")

    # ── Hostes (~2-4 per reserva) ────────────────────────────────────────────
    # Per cada reserva creem un hoste principal (a partir de l'inquili) i
    # 1-3 hostes addicionals amb dades coherents.
    hostes_extra = [
        # (nom, genere, relacio, doc_type, doc_num, nacionalitat, naixement, residencia, email, tel)
        ("Aina Puig Coma",       "Dona",  "Parella",        "DNI",       "11112222Z", "Espanyola",  "1995-03-12", "Carrer Major 5, Barcelona",      "aina.puig@gmail.com",     "+34 600 000 001"),
        ("Eric Bosch Pons",      "Home",  "Fill/a",         "DNI",       "22223333Y", "Espanyola",  "2015-07-22", "Carrer Major 5, Barcelona",      "",                        ""),
        ("Maria Solans Roca",    "Dona",  "Fill/a",         "DNI",       "33334444X", "Espanyola",  "2018-11-04", "Avinguda Diagonal 10, Barcelona","",                        ""),
        ("Pau Llopis Vila",      "Home",  "Parella",        "Passaport", "AB1234567", "Francesa",   "1988-01-30", "Rue de la Paix 12, Paris",       "pau.llopis@gmail.com",    "+33 6 12 34 56 78"),
        ("Clara Ferrer Mas",     "Dona",  "Germà/Germana",  "DNI",       "44445555W", "Espanyola",  "1993-06-18", "Placa Catalunya 8, Tarragona",   "clara.ferrer@gmail.com",  "+34 600 000 002"),
        ("Roger Pla Font",       "Home",  "Fill/a",         "DNI",       "55556666V", "Espanyola",  "2012-04-09", "Carrer del Pi 12, Lleida",       "",                        ""),
        ("Laia Vidal Mas",       "Dona",  "Parella",        "NIE",       "Y1234567B", "Argentina",  "1991-09-25", "Rambla Nova 20, Tarragona",      "laia.vidal@gmail.com",    "+54 11 1234 5678"),
        ("Marti Coll Vives",     "Home",  "Fill/a",         "DNI",       "66667777U", "Espanyola",  "2019-02-14", "Carrer Balmes 55, Barcelona",    "",                        ""),
        ("Berta Sole Pons",      "Dona",  "Parella",        "DNI",       "77778888T", "Espanyola",  "1986-12-01", "Via Augusta 3, Barcelona",       "berta.sole@gmail.com",    "+34 600 000 003"),
        ("Nil Camps Ros",        "Home",  "Parella",        "DNI",       "88889999S", "Espanyola",  "1990-08-15", "Carrer Groc 7, Reus",            "nil.camps@gmail.com",     "+34 600 000 004"),
        ("Quim Sala Mas",        "Home",  "Fill/a",         "DNI",       "99990000R", "Espanyola",  "2014-05-20", "Passeig de la Pau 1, Vic",       "",                        ""),
        ("Mireia Roca Pla",      "Dona",  "Parella",        "DNI",       "00001111Q", "Espanyola",  "1992-10-03", "Carrer dels Albers 4, Manresa",  "mireia.roca@gmail.com",   "+34 600 000 005"),
    ]

    total_hostes = 0
    # Patró d'addicionals per reserva (índexs a hostes_extra). Ciclat per 20 reserves.
    patrons = [
        [0, 1, 2],     # 1 + 3 → 4
        [3],           # 1 + 1 → 2
        [4, 5],        # 1 + 2 → 3
        [],            # 1 → 1
        [6, 7, 8],     # 1 + 3 → 4
        [9],
        [10, 11],
        [0],
        [1, 2],
        [],
        [3, 4],
        [5],
        [6, 7, 8],
        [9, 10],
        [0],
        [1],
        [2, 3, 4],
        [5, 6],
        [],
        [7, 8],
    ]

    for idx, reserva in enumerate(reserves):
        inq = reserva.inquili
        # Hoste principal (basat en l'inquili)
        Hoste.objects.create(
            reserva=reserva,
            es_principal=True,
            nom_complet=inq.nom_complet,
            genere="Home" if idx % 2 == 0 else "Dona",
            tipus_document="DNI",
            numero_document=inq.dni_passaport,
            nacionalitat="Espanyola",
            data_naixement=f"19{70 + (idx % 30):02d}-0{1 + (idx % 9)}-15",
            residencia=inq.residencia,
            email=inq.email,
            telefon=f"+34 6{idx:02d} 000 000",
        )
        total_hostes += 1

        # Hostes addicionals
        for extra_idx in patrons[idx]:
            extra = hostes_extra[extra_idx]
            (nom, gen, rel, dtype, dnum, nac, naix, res, em, tel) = extra
            Hoste.objects.create(
                reserva=reserva,
                es_principal=False,
                nom_complet=nom,
                genere=gen,
                relacio_parental=rel,
                tipus_document=dtype,
                numero_document=dnum,
                nacionalitat=nac,
                data_naixement=naix,
                residencia=res,
                email=em,
                telefon=tel,
            )
            total_hostes += 1

        # Actualitzar el comptador a la reserva
        reserva.num_hostes = reserva.hostes.count()
        reserva.save(update_fields=['num_hostes'])

    print(f"{total_hostes} hostes creats")

    # ── Pagaments de reserves ────────────────────────────────────────────────
    # Format: (reserva_idx, data_pagament, import_pagament, metode, estat)
    # Les reserves pagades (pagat=True) tenen 1-2 pagaments en estat 'pagat'.
    # Algunes reserves no pagades tenen 1 pagament en estat 'pendent' o 'cancelat'.
    pagaments_data = [
        # Reserva 0 · Apartament Gracia Centre · 5 nits · Airbnb · pagada
        (0,  "2026-01-08",  550.00, "targeta",       "pagat"),
        # Reserva 1 · Atic Vista Mar · 3 nits · Booking · pagada
        (1,  "2026-01-18",  660.00, "transferencia", "pagat"),
        # Reserva 2 · Casa amb jardi Sitges · 7 nits · Direct · pagada (2 pagaments)
        (2,  "2026-01-20", 1225.00, "transferencia", "pagat"),
        (2,  "2026-02-01", 1225.00, "transferencia", "pagat"),
        # Reserva 3 · Estudi Barceloneta · 2 nits · Airbnb · NO pagada
        (3,  "2026-02-12",  150.00, "bizum",         "pendent"),
        # Reserva 4 · Xalet Costa Brava · 7 nits · Direct · pagada (2 pagaments)
        (4,  "2026-02-10", 1680.00, "transferencia", "pagat"),
        (4,  "2026-02-25", 1680.00, "transferencia", "pagat"),
        # Reserva 5 · Pis Modern Eixample · 3 nits · Booking · NO pagada
        (5,  "2026-03-14",  450.00, "targeta",       "pendent"),
        # Reserva 6 · Apartament Girona Vella · 2 nits · Airbnb · pagada
        (6,  "2026-04-03",  190.00, "targeta",       "pagat"),
        # Reserva 7 · Duplex Tarragona Mar · 5 nits · Direct · NO pagada (cancelat)
        (7,  "2026-04-18",  900.00, "transferencia", "cancelat"),
        # Reserva 8 · Casa Rural Osona · 4 nits · Booking · pagada
        (8,  "2026-04-28", 1200.00, "transferencia", "pagat"),
        # Reserva 9 · Apartament Lleida Centre · 7 nits · Airbnb · NO pagada
        (9,  "2026-05-08",  490.00, "bizum",         "pendent"),
        # Reserva 10 · Atic Terrassa Vista · 2 nits · Direct · pagada
        (10, "2026-05-18",  260.00, "efectiu",       "pagat"),
        # Reserva 11 · Pis Badalona Platja · 7 nits · Booking · NO pagada
        (11, "2026-05-28",  840.00, "targeta",       "pendent"),
        # Reserva 12 · Casa Adossada Sabadell · 5 nits · Airbnb · pagada
        (12, "2026-06-12",  800.00, "transferencia", "pagat"),
        # Reserva 13 · Estudi Mataro Rambla · 6 nits · Altres · NO pagada
        (13, "2026-06-28",  390.00, "altres",        "pendent"),
        # Reserva 14 · Apartament Manresa Nou · 4 nits · Direct · pagada
        (14, "2026-07-08",  320.00, "bizum",         "pagat"),
        # Reserva 15 · Xalet Roses Costa · 5 nits · Booking · NO pagada
        (15, "2026-07-18", 2000.00, "transferencia", "pendent"),
        # Reserva 16 · Pis Figueres Rambla · 9 nits · Airbnb · pagada
        (16, "2026-07-30",  765.00, "targeta",       "pagat"),
        # Reserva 17 · Casa Rural Priorat · 3 nits · Direct · pagada
        (17, "2026-08-13",  780.00, "transferencia", "pagat"),
        # Reserva 18 · Apartament Tortosa Riu · 4 nits · Booking · NO pagada
        (18, "2026-08-28",  300.00, "bizum",         "pendent"),
        # Reserva 19 · Duplex Vilanova Centre · 5 nits · Airbnb · pagada
        (19, "2026-09-08",  975.00, "targeta",       "pagat"),
    ]

    pagaments = [
        PagamentReserva.objects.create(
            reserva=reserves[r_idx],
            data_pagament=data,
            import_pagament=imp,
            metode_pagament=metode,
            estat=estat,
        )
        for r_idx, data, imp, metode, estat in pagaments_data
    ]
    print(f"{len(pagaments)} pagaments creats")
    print("Tot OK!")


if __name__ == "__main__":
    run()
