from django.urls import path
from . import views

urlpatterns = [
    path('', views.ImmobleListCreateView.as_view(), name='immoble-list'),
    path('<int:pk>/', views.ImmobleDetailView.as_view(), name='immoble-detail'),
    path('<int:immoble_pk>/temporades/', views.TemporadaListCreateView.as_view(), name='temporada-list'),
]
