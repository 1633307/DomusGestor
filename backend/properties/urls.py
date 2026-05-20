from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImmobleListCreateView.as_view(), name='immoble-list'),
    path('serveis/', views.ServeiListView.as_view(), name='immoble-servei-list'),
    path('<int:pk>/', views.ImmobleDetailView.as_view(), name='immoble-detail'),
    path('<int:pk>/pagaments/', views.ImmobleHistoricPagamentsView.as_view(), name='immoble-pagaments'),
]
