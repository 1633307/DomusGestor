"""
Seed script: crea 20 immobles, 20 inquilins i 20 reserves de mostra.
Executa'l des de la carpeta backend/:

    python seed_data.py

AVÍS: esborra tots els registres existents de reserves, inquilins i immobles
abans de crear-ne de nous.

REQUISIT PREVI, EXECUTAR A LA CARPETA DE BACKEND: python manage.py migrate
"""



import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "domusgestor.settings")
django.setup()

from properties.models import Immoble
from bookings.models import InquiliBasic, ReservaBasica


def run():
    # ── Netejar dades existents ──────────────────────────────────────────────
    deleted_r = ReservaBasica.objects.all().delete()[0]
    deleted_i = InquiliBasic.objects.all().delete()[0]
    deleted_m = Immoble.objects.all().delete()[0]
    print(f"Eliminats: {deleted_r} reserves, {deleted_i} inquilins, {deleted_m} immobles")

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

    immobles = []
    for row in immobles_data:
        (nom, ref, adr, ciutat, cp, tipus, cap, hab, banys, m2, preu, actiu,
         prop_nom, prop_dni, prop_email, prop_tel, prop_adr, prop_iban) = row
        imm = Immoble.objects.create(
            nom_comercial=nom, referencia=ref, adreca=adr, ciutat=ciutat,
            codi_postal=cp, tipus_immoble=tipus, capacitat_maxima=cap,
            num_habitacions=hab, num_banys=banys, metres_quadrats=m2,
            preu_base_nit=preu, actiu=actiu,
            propietari_nom=prop_nom, propietari_dni=prop_dni,
            propietari_email=prop_email, propietari_telefon=prop_tel,
            propietari_adreca=prop_adr, propietari_iban=prop_iban,
        )
        immobles.append(imm)

    print(f"{len(immobles)} immobles creats")

    # ── 20 Inquilins ─────────────────────────────────────────────────────────
    # DNIs ficticis (no coincideixen amb els propietaris per evitar colisions)
    inquilins_data = [
        ("Marc Rovira Puig",      "98765432A", "marc.rovira@gmail.com",    "Carrer Major, 5, Barcelona"),
        ("Laia Font Soler",       "87654321B", "laia.font@hotmail.com",    "Avinguda Diagonal, 10, Barcelona"),
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
    for nom, dni, email, facturacio in inquilins_data:
        inq = InquiliBasic.objects.create(
            nom_complet=nom,
            dni_passaport=dni,
            email=email,
            dades_facturacio=facturacio,
        )
        inquilins.append(inq)

    print(f"{len(inquilins)} inquilins creats")

    # ── 20 Reserves ──────────────────────────────────────────────────────────
    # Cada fila: (index_immoble, index_inquili, data_entrada, data_sortida, pagat)
    reserves_data = [
        (0,  0,  "2026-01-10", "2026-01-15", True),
        (1,  1,  "2026-01-20", "2026-01-23", True),
        (2,  2,  "2026-02-03", "2026-02-10", True),
        (3,  3,  "2026-02-14", "2026-02-16", False),
        (4,  4,  "2026-03-01", "2026-03-08", True),
        (5,  5,  "2026-03-15", "2026-03-18", False),
        (6,  6,  "2026-04-05", "2026-04-07", True),
        (7,  7,  "2026-04-20", "2026-04-25", False),
        (8,  8,  "2026-05-01", "2026-05-05", True),
        (9,  9,  "2026-05-10", "2026-05-17", False),
        (10, 10, "2026-05-20", "2026-05-22", True),
        (11, 11, "2026-06-01", "2026-06-08", False),
        (12, 12, "2026-06-15", "2026-06-20", True),
        (13, 13, "2026-07-01", "2026-07-07", False),
        (14, 14, "2026-07-10", "2026-07-14", True),
        (15, 15, "2026-07-20", "2026-07-25", False),
        (16, 16, "2026-08-01", "2026-08-10", True),
        (17, 17, "2026-08-15", "2026-08-18", True),
        (18, 18, "2026-09-01", "2026-09-05", False),
        (19, 19, "2026-09-10", "2026-09-15", True),
    ]

    reserves = []
    for imm_i, inq_i, entrada, sortida, pagat in reserves_data:
        r = ReservaBasica.objects.create(
            immoble=immobles[imm_i],
            inquili=inquilins[inq_i],
            data_entrada=entrada,
            data_sortida=sortida,
            pagat=pagat,
        )
        reserves.append(r)

    print(f"{len(reserves)} reserves creades")
    print("Tot OK!")


if __name__ == "__main__":
    run()
