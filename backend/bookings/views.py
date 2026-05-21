from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

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
