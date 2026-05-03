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
    def get_queryset(self):
        # Agafem la llista original d'immobles
        queryset = super().get_queryset()

        # Capturem els parametres
        filtro_ciutat = self.request.query_params.get('ciutat')
        filtro_habit = self.request.query_params.get('habitacions')
        dataini_filtre = self.request.query_params.get('dataini')
        datafi_filtre = self.request.query_params.get('datafi')
        
        if filtro_ciutat:
            queryset = queryset.filter(ciutat__icontains=filtro_ciutat)
            
        if filtro_habit:
            queryset = queryset.filter(num_habitacions__gte=filtro_habit)

        if dataini_filtre and datafi_filtre:
            reservas_solapadas = ReservaBasica.objects.filter(
                data_entrada__lt=datafi_filtre,
                data_sortida__gt=dataini_filtre
            )
            queryset = queryset.exclude(id__in=reservas_solapadas.values('immoble_id'))
            
        return queryset



class ImmobleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF-01: Detall, actualització i eliminació d'immoble."""
    queryset = Immoble.objects.all()
    serializer_class = ImmobleSerializer
