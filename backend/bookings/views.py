<<<<<<< HEAD
from datetime import date, timedelta

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework import generics
=======
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
>>>>>>> 728d399ca371f0b700cf3ff6bfa8cf3f1ad1ba16
from rest_framework.response import Response
from rest_framework.views import APIView

from core.fields import hmac_value
from properties.models import Immoble

from .emails import enviar_comunicacio_manual
from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Comunicacio, ComunicacioEmail
from .serializers import (
    PersonaSerializer, PerfilPropietariSerializer,
    ReservaSerializer, ComunicacioSerializer, ComunicacioEmailSerializer, DashboardSerializer,
)
from .services import calcular_preview_reserva


class PersonaListCreateView(generics.ListCreateAPIView):
    queryset = (
        Persona.objects
        .select_related('perfil_inquili', 'perfil_propietari')
        .order_by('nom_complet')
    )
    serializer_class = PersonaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        document = self.request.query_params.get('document')
        if document:
            from core.fields import hmac_value
            queryset = queryset.filter(dni_passaport_hash=hmac_value(document))
        return queryset


class PersonaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Persona.objects
        .select_related('perfil_inquili', 'perfil_propietari')
        .prefetch_related('reserves__immoble')
        .all()
    )
    serializer_class = PersonaSerializer


class PerfilPropietariListCreateView(generics.ListCreateAPIView):
    queryset = PerfilPropietari.objects.select_related('persona').all()
    serializer_class = PerfilPropietariSerializer


class PerfilPropietariDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PerfilPropietari.objects.select_related('persona').all()
    serializer_class = PerfilPropietariSerializer


class ReservaListCreateView(generics.ListCreateAPIView):
    queryset = (
        ReservaBasica.objects
        .select_related('immoble', 'inquili')
        .prefetch_related('hostes')
        .all()
    )
    serializer_class = ReservaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        filtro_reserva = self.request.query_params.get('reserva')
        if filtro_reserva:
            queryset = queryset.filter(id=filtro_reserva)
        filtro_immoble = self.request.query_params.get('immoble')
        if filtro_immoble:
            queryset = queryset.filter(immoble_id=filtro_immoble)
        filtro_inquili = self.request.query_params.get('inquili')
        if filtro_inquili:
            queryset = queryset.filter(inquili_id=filtro_inquili)
        return queryset


class ReservaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        ReservaBasica.objects
        .select_related('immoble', 'inquili')
        .prefetch_related('hostes')
        .all()
    )
    serializer_class = ReservaSerializer


class ComunicacioListCreateView(generics.ListCreateAPIView):
    serializer_class = ComunicacioSerializer

    def get_queryset(self):
        return Comunicacio.objects.filter(reserva_id=self.kwargs['reserva_pk'])

    def perform_create(self, serializer):
        comunicacio = serializer.save(reserva_id=self.kwargs['reserva_pk'])
        if comunicacio.canal == 'Email':
            enviar_comunicacio_manual(
                reserva=comunicacio.reserva,
                comunicacio=comunicacio,
                usuari=self.request.user,
            )


class ComunicacioDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComunicacioSerializer

    def get_queryset(self):
        return Comunicacio.objects.filter(reserva_id=self.kwargs['reserva_pk'])


class ComunicacioEmailListView(generics.ListAPIView):
    serializer_class = ComunicacioEmailSerializer

    def get_queryset(self):
        return ComunicacioEmail.objects.filter(reserva_id=self.kwargs['reserva_pk'])


class ReservaPreviewView(APIView):
    def post(self, request):
        return Response(calcular_preview_reserva(request.data))


class ClientPortalLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        codi_reserva = str(request.data.get('codi_reserva', '')).strip()
        nip = str(request.data.get('nip', '')).strip()

        if not codi_reserva or not nip:
            return Response(
                {'detail': 'Cal indicar el numero de reserva i el NIP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            ReservaBasica.objects
            .select_related('immoble', 'inquili')
            .prefetch_related('hostes__persona')
        )
        reserva = queryset.filter(codi_reserva__iexact=codi_reserva).first()
        if reserva is None and codi_reserva.isdigit():
            reserva = queryset.filter(pk=int(codi_reserva)).first()

        if reserva is None or not self._nip_matches_reserva(reserva, nip):
            return Response(
                {'detail': 'No hem pogut verificar la reserva amb aquestes dades.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(self._serialize_reserva(reserva))

    def _nip_matches_reserva(self, reserva, nip):
        nip_hash = hmac_value(nip)
        if reserva.inquili.dni_passaport_hash == nip_hash:
            return True

        normalized_nip = nip.casefold()
        for hoste in reserva.hostes.all():
            if hoste.numero_document.strip().casefold() == normalized_nip:
                return True
            if hoste.persona and hoste.persona.dni_passaport_hash == nip_hash:
                return True
        return False

    def _serialize_reserva(self, reserva):
        hostes = [
            {
                'id': hoste.id,
                'nom_complet': hoste.nom_complet,
                'es_principal': hoste.es_principal,
                'nacionalitat': hoste.nacionalitat,
            }
            for hoste in reserva.hostes.all()
        ]
        return {
            'id': reserva.id,
            'codi_reserva': reserva.codi_reserva,
            'immoble_nom': reserva.immoble.nom_comercial,
            'inquili_nom': reserva.inquili.nom_complet,
            'data_entrada': reserva.data_entrada,
            'data_sortida': reserva.data_sortida,
            'num_hostes': reserva.num_hostes or len(hostes),
            'hostes': hostes,
            'tipus_reserva': reserva.tipus_reserva,
            'estat_reserva': reserva.estat_reserva,
            'pagat': reserva.pagat,
            'estat_pagament': reserva.estat_pagament,
            'import_total': reserva.import_total,
            'import_pagat': reserva.import_pagat,
            'import_pendent': reserva.import_pendent,
            'fianca': reserva.fianca,
            'metode_pagament': reserva.metode_pagament,
            'data_ultim_pagament': reserva.data_ultim_pagament,
            'observacions_pagament': reserva.observacions_pagament,
        }


class DashboardView(APIView):
    def get(self, request):
        avui = date.today()

        m = avui.month - 5
        y = avui.year
        while m <= 0:
            m += 12
            y -= 1
        inici_6_mesos = date(y, m, 1)

        mensuals_qs = (
            ReservaBasica.objects
            .filter(data_entrada__gte=inici_6_mesos)
            .annotate(mes_trunc=TruncMonth('data_entrada'))
            .values('mes_trunc')
            .annotate(ingressos=Sum('import_pagat'))
            .order_by('mes_trunc')
        )
        ingressos_dict = {
            row['mes_trunc'].strftime('%Y-%m'): float(row['ingressos'] or 0)
            for row in mensuals_qs
        }
        ingressos_per_mes = []
        for i in range(5, -1, -1):
            mi = avui.month - i
            yi = avui.year
            while mi <= 0:
                mi += 12
                yi -= 1
            key = f"{yi:04d}-{mi:02d}"
            ingressos_per_mes.append({'mes': key, 'ingressos': ingressos_dict.get(key, 0)})

        estats = ['prereservada', 'reservada', 'lista', 'cancelada']
        reserves_per_estat = {
            estat: ReservaBasica.objects.filter(estat_reserva=estat).count()
            for estat in estats
        }

        data = {
            'total_reserves': ReservaBasica.objects.count(),
            'total_immobles': Immoble.objects.count(),
            'total_inquilins': PerfilInquili.objects.count(),
            'immobles_actius': Immoble.objects.filter(actiu=True).count(),
            'reserves_pagades': ReservaBasica.objects.filter(pagat=True).count(),
            'ingressos_totals': ReservaBasica.objects.aggregate(
                total=Sum('import_pagat')
            )['total'] or 0,
            'reserves_proximes_7_dies': ReservaBasica.objects.filter(
                data_entrada__range=[avui, avui + timedelta(days=7)]
            ).count(),
            'reserves_per_estat': reserves_per_estat,
            'ingressos_per_mes': ingressos_per_mes,
        }
        return Response(DashboardSerializer(data).data)


class RendimentPropietariView(APIView):
    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        from django.db.models import Count
        persona = get_object_or_404(Persona, pk=pk)
        if not hasattr(persona, 'perfil_propietari'):
            return Response(
                {'detail': 'Aquesta persona no és propietari.'},
                status=400,
            )

        immobles = list(
            Immoble.objects
            .filter(propietari=persona)
            .annotate(
                num_reserves=Count('reserves'),
                ingressos_sum=Sum('reserves__import_pagat'),
            )
        )

        ingressos_totals = sum(float(i.ingressos_sum or 0) for i in immobles)

        return Response({
            'num_immobles': len(immobles),
            'immobles_actius': sum(1 for i in immobles if i.actiu),
            'total_reserves': sum(i.num_reserves for i in immobles),
            'ingressos_totals': f"{ingressos_totals:.2f}",
            'reserves_per_immoble': [
                {
                    'id': i.id,
                    'nom': i.nom_comercial,
                    'num_reserves': i.num_reserves,
                    'ingressos': f"{float(i.ingressos_sum or 0):.2f}",
                    'actiu': i.actiu,
                }
                for i in immobles
            ],
        })
