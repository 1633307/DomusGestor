from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('me/', views.MeView.as_view(), name='me'),
    path('propietaris/', views.PropietariListCreateView.as_view(), name='propietari-list'),
    path('propietaris/<int:pk>/', views.PropietariDetailView.as_view(), name='propietari-detail'),
]
