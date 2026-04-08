from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.models import Immoble
from .models import Inquili, Reserva
from .serializers import InquiliSerializer, ReservaSerializer, DashboardSerializer


class InquiliListCreateView(generics.ListCreateAPIView):
    queryset = Inquili.objects.all()
    serializer_class = InquiliSerializer


class InquiliDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inquili.objects.all()
    serializer_class = InquiliSerializer


class ReservaListCreateView(generics.ListCreateAPIView):
    queryset = Reserva.objects.select_related('immoble', 'inquili_principal').prefetch_related('hostes__hoste').all()
    serializer_class = ReservaSerializer


class ReservaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reserva.objects.select_related('immoble', 'inquili_principal').prefetch_related('hostes__hoste').all()
    serializer_class = ReservaSerializer


class DashboardView(APIView):
    def get(self, request):
        data = {
            'total_reserves': Reserva.objects.count(),
            'total_immobles': Immoble.objects.count(),
            'total_inquilins': Inquili.objects.count(),
            'immobles_actius': Immoble.objects.filter(actiu=True).count(),
            'reserves_confirmades': Reserva.objects.filter(estat='confirmada').count(),
        }
        serializer = DashboardSerializer(data)
        return Response(serializer.data)
