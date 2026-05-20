from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.models import Immoble
from .models import InquiliBasic, ReservaBasica
from .serializers import InquiliSerializer, ReservaSerializer, DashboardSerializer
from .services import calcular_preview_reserva


class InquiliListCreateView(generics.ListCreateAPIView):
    queryset = InquiliBasic.objects.all()
    serializer_class = InquiliSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        document = self.request.query_params.get('document')
        if document:
            from core.fields import hmac_value
            queryset = queryset.filter(dni_passaport_hash=hmac_value(document))
        return queryset


class InquiliDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InquiliBasic.objects.all()
    serializer_class = InquiliSerializer


class ReservaListCreateView(generics.ListCreateAPIView):
    """RF-23: Llista i crea reserves."""
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
            
        return queryset


class ReservaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF-23: Detall, actualització i eliminació de reserva (incl. hostes)."""
    queryset = (
        ReservaBasica.objects
        .select_related('immoble', 'inquili')
        .prefetch_related('hostes')
        .all()
    )
    serializer_class = ReservaSerializer


class ReservaPreviewView(APIView):
    """Calcula el resum economic d'una reserva sense desar cap dada."""

    def post(self, request):
        return Response(calcular_preview_reserva(request.data))


class DashboardView(APIView):
    def get(self, request):
        data = {
            'total_reserves': ReservaBasica.objects.count(),
            'total_immobles': Immoble.objects.count(),
            'total_inquilins': InquiliBasic.objects.count(),
            'immobles_actius': Immoble.objects.filter(actiu=True).count(),
            'reserves_pagades': ReservaBasica.objects.filter(pagat=True).count(),
        }
        return Response(DashboardSerializer(data).data)
