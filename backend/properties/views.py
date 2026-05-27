import logging

from rest_framework import generics, filters

from .models import Immoble, Servei
from .serializers import ImmobleSerializer, ServeiSerializer
from bookings.models import ReservaBasica, PagamentReserva
from bookings.serializers import PagamentReservaSerializer

logger = logging.getLogger(__name__)


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
        capacitat_filtre = self.request.query_params.get('capacitat')
        if filtro_ciutat:
            queryset = queryset.filter(ciutat__icontains=filtro_ciutat)
        if capacitat_filtre:
            queryset = queryset.filter(capacitat_maxima__gte=capacitat_filtre)

        if filtro_habit:
            queryset = queryset.filter(num_habitacions__gte=filtro_habit)

        if dataini_filtre and datafi_filtre:
            reservas_solapadas = ReservaBasica.objects.filter(
                data_entrada__lt=datafi_filtre,
                data_sortida__gt=dataini_filtre
            )
            queryset = queryset.exclude(
                id__in=reservas_solapadas.values('immoble_id'))

        return queryset

    def perform_create(self, serializer):
        super().perform_create(serializer)
        logger.info('Immoble creat: id=%s nom=%s', serializer.instance.pk, serializer.instance.nom_comercial)


class ImmobleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF-01: Detall, actualització i eliminació d'immoble."""
    queryset = Immoble.objects.all()
    serializer_class = ImmobleSerializer

    def perform_update(self, serializer):
        super().perform_update(serializer)
        logger.info('Immoble actualitzat: id=%s', serializer.instance.pk)

    def perform_destroy(self, instance):
        logger.info('Immoble eliminat: id=%s nom=%s', instance.pk, instance.nom_comercial)
        super().perform_destroy(instance)


class ServeiListView(generics.ListAPIView):
    queryset = Servei.objects.all()
    serializer_class = ServeiSerializer


class ImmobleHistoricPagamentsView(generics.ListAPIView):
    serializer_class = PagamentReservaSerializer

    def get_queryset(self):
        return (
            PagamentReserva.objects
            .filter(reserva__immoble_id=self.kwargs['pk'])
            .select_related('reserva', 'reserva__inquili')
        )
