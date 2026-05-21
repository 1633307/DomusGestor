from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction

from bookings.models import ReservaBasica
from bookings.serializers import sync_persona_from_hoste


class Command(BaseCommand):
    help = "Sincronitza dades buides d'inquilins a partir de l'hoste principal de cada reserva."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra què es canviaria sense guardar cap canvi.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Sobrescriu camps existents. Per defecte només omple camps buits.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        overwrite = options['overwrite']

        reservas_revisades = 0
        inquilins_actualitzats = set()
        camps_emplenats = Counter()
        sense_inquili = 0
        sense_hoste_principal = 0

        queryset = (
            ReservaBasica.objects
            .select_related('inquili')
            .prefetch_related('hostes')
            .order_by('id')
        )

        with transaction.atomic():
            for reserva in queryset:
                reservas_revisades += 1

                if not reserva.inquili_id:
                    sense_inquili += 1
                    continue

                hoste_principal = next(
                    (hoste for hoste in reserva.hostes.all() if hoste.es_principal),
                    None,
                )
                if hoste_principal is None:
                    sense_hoste_principal += 1
                    continue

                changed_fields = sync_persona_from_hoste(
                    reserva.inquili,
                    hoste_principal,
                    overwrite=overwrite,
                )

                if changed_fields:
                    inquilins_actualitzats.add(reserva.inquili_id)
                    camps_emplenats.update(changed_fields)

            if dry_run:
                transaction.set_rollback(True)

        mode = 'DRY-RUN' if dry_run else 'APLICAT'
        overwrite_text = 'amb overwrite' if overwrite else 'sense overwrite'
        self.stdout.write(self.style.SUCCESS(f'Sincronització {mode} ({overwrite_text})'))
        self.stdout.write(f'Reserves revisades: {reservas_revisades}')
        self.stdout.write(f'Inquilins actualitzats: {len(inquilins_actualitzats)}')
        self.stdout.write(f'Registres saltats sense inquilí: {sense_inquili}')
        self.stdout.write(f'Registres saltats sense hoste principal: {sense_hoste_principal}')

        if camps_emplenats:
            self.stdout.write('Camps emplenats:')
            for field_name, count in sorted(camps_emplenats.items()):
                self.stdout.write(f'  - {field_name}: {count}')
        else:
            self.stdout.write('Camps emplenats: 0')
