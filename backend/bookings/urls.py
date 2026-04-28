from django.urls import path
from . import views

urlpatterns = [
    path('reserves/', views.ReservaListCreateView.as_view(), name='reserva-list'),
    path('reserves/<int:pk>/', views.ReservaDetailView.as_view(), name='reserva-detail'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
