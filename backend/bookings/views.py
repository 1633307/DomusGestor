from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.fields import hmac_value
from properties.models import Immoble

from .models import Persona, PerfilInquili, PerfilPropietari, ReservaBasica, Comunicacio
from .serializers import (
    PersonaSerializer, PerfilPropietariSerializer,
    ReservaSerializer, ComunicacioSerializer, DashboardSerializer,
)
from .services import calcular_preview_reserva


class PersonaListCreateView(generics.ListCreateAPIView):
    queryset = Persona.objects.all().order_by('nom_complet')
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
        serializer.save(reserva_id=self.kwargs['reserva_pk'])


class ComunicacioDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ComunicacioSerializer

    def get_queryset(self):
        return Comunicacio.objects.filter(reserva_id=self.kwargs['reserva_pk'])


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
        data = {
            'total_reserves': ReservaBasica.objects.count(),
            'total_immobles': Immoble.objects.count(),
            'total_inquilins': PerfilInquili.objects.count(),
            'immobles_actius': Immoble.objects.filter(actiu=True).count(),
            'reserves_pagades': ReservaBasica.objects.filter(pagat=True).count(),
        }
        return Response(DashboardSerializer(data).data)
