from rest_framework import generics, filters

from .models import Immoble
from .serializers import ImmobleSerializer


class ImmobleListCreateView(generics.ListCreateAPIView):
    """RF-01, RF-13: Llista i crea immobles."""
    queryset = Immoble.objects.all()
    serializer_class = ImmobleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom_comercial', 'adreca']
    ordering_fields = ['nom_comercial', 'preu_base_nit', 'data_registre']
    ordering = ['-data_registre']


class ImmobleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF-01: Detall, actualització i eliminació d'immoble."""
    queryset = Immoble.objects.all()
    serializer_class = ImmobleSerializer
