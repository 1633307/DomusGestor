from django.urls import path
from . import views

urlpatterns = [
    path('persones/', views.PersonaListCreateView.as_view(), name='persona-list'),
    path('persones/<int:pk>/', views.PersonaDetailView.as_view(), name='persona-detail'),
    path('perfils-propietari/', views.PerfilPropietariListCreateView.as_view(), name='perfil-propietari-list'),
    path('perfils-propietari/<int:pk>/', views.PerfilPropietariDetailView.as_view(), name='perfil-propietari-detail'),
    path('reserves/', views.ReservaListCreateView.as_view(), name='reserva-list'),
    path('reserves/preview/', views.ReservaPreviewView.as_view(), name='reserva-preview'),
    path('client-portal/login/', views.ClientPortalLoginView.as_view(), name='client-portal-login'),
    path('client-portal/pay/', views.ClientPortalPayView.as_view(), name='client-portal-pay'),
    path('reserves/<int:pk>/', views.ReservaDetailView.as_view(), name='reserva-detail'),
    path(
        'reserves/<int:reserva_pk>/comunicacions/',
        views.ComunicacioListCreateView.as_view(),
        name='comunicacio-list',
    ),
    path(
        'reserves/<int:reserva_pk>/comunicacions/<int:pk>/',
        views.ComunicacioDetailView.as_view(),
        name='comunicacio-detail',
    ),
    path(
        'reserves/<int:reserva_pk>/emails/',
        views.ComunicacioEmailListView.as_view(),
        name='comunicacio-email-list',
    ),
    path('reserves/<int:pk>/fitxa-viatger/', views.FitxaViatgerPDFView.as_view(), name='fitxa-viatger'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('persones/<int:pk>/rendiment/', views.RendimentPropietariView.as_view(), name='rendiment-propietari'),
]
