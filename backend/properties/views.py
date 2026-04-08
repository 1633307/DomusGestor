from rest_framework import generics, filters
from .models import Immoble, Temporada
from .serializers import ImmobleSerializer, ImmobleCreateSerializer, TemporadaSerializer


class ImmobleListCreateView(generics.ListCreateAPIView):
    queryset = Immoble.objects.select_related('propietari').prefetch_related('temporades').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom_comercial', 'adreca']
    ordering_fields = ['nom_comercial', 'preu_base', 'data_registre']
    ordering = ['-data_registre']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ImmobleCreateSerializer
        return ImmobleSerializer


class ImmobleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Immoble.objects.select_related('propietari').prefetch_related('temporades').all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ImmobleCreateSerializer
        return ImmobleSerializer


class TemporadaListCreateView(generics.ListCreateAPIView):
    serializer_class = TemporadaSerializer

    def get_queryset(self):
        return Temporada.objects.filter(immoble_id=self.kwargs['immoble_pk'])

    def perform_create(self, serializer):
        serializer.save(immoble_id=self.kwargs['immoble_pk'])
