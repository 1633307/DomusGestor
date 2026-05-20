from django.urls import path
from . import views

urlpatterns = [
    path('inquilins/', views.InquiliListCreateView.as_view(), name='inquili-list'),
    path('inquilins/<int:pk>/', views.InquiliDetailView.as_view(), name='inquili-detail'),
    path('reserves/', views.ReservaListCreateView.as_view(), name='reserva-list'),
    path('reserves/preview/', views.ReservaPreviewView.as_view(), name='reserva-preview'),
    path('reserves/<int:pk>/', views.ReservaDetailView.as_view(), name='reserva-detail'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]
