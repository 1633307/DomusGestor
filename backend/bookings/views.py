from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.models import Immoble
from .models import InquiliBasic, ReservaBasica
from .serializers import InquiliSerializer, ReservaSerializer, DashboardSerializer


class InquiliListCreateView(generics.ListCreateAPIView):
    """RF-17, RF-18, RF-25: Llista i crea inquilins."""
    queryset = InquiliBasic.objects.all()
    serializer_class = InquiliSerializer


class InquiliDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF-17: Detall, actualització i eliminació d'inquilí."""
    queryset = InquiliBasic.objects.all()
    serializer_class = InquiliSerializer


class ReservaListCreateView(generics.ListCreateAPIView):
    """RF-23: Llista i crea reserves."""
    queryset = ReservaBasica.objects.select_related('immoble', 'inquili').all()
    serializer_class = ReservaSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        filtro_reserva = self.request.query_params.get('reserva')
        if filtro_reserva:
            queryset = queryset.filter(id=filtro_reserva)
        return queryset


class ReservaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF-23: Detall, actualització i eliminació de reserva."""
    queryset = ReservaBasica.objects.select_related('immoble', 'inquili').all()
    serializer_class = ReservaSerializer


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
