import logging

from django.http import Http404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Usuari, InfoImmobiliaria
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UsuariSerializer,
    CreateUsuariSerializer,
    UpdateUsuariSerializer,
    InfoImmobiliariaSerializer,
)

logger = logging.getLogger(__name__)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user  = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        logger.info('Inici de sessió: user_id=%s', user.pk)
        return Response({'token': token.key, 'user': UsuariSerializer(user).data})


class LogoutView(APIView):
    def post(self, request):
        logger.info('Tancament de sessió: user_id=%s', request.user.pk)
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(generics.CreateAPIView):
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user  = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        logger.info('Nou registre: user_id=%s', user.pk)
        return Response(
            {'token': token.key, 'user': UsuariSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    def get(self, request):
        return Response(UsuariSerializer(request.user).data)


class UserListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = Usuari.objects.all().order_by('-date_joined')
        return Response(UsuariSerializer(users, many=True).data)

    def post(self, request):
        serializer = CreateUsuariSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info('Admin crea usuari: nou_user_id=%s admin_id=%s', user.pk, request.user.pk)
        return Response(UsuariSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAdmin]

    def get_object(self, pk):
        try:
            return Usuari.objects.get(pk=pk)
        except Usuari.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        return Response(UsuariSerializer(self.get_object(pk)).data)

    def put(self, request, pk):
        user = self.get_object(pk)
        if request.user.pk == pk and not request.data.get('is_admin', True):
            return Response(
                {'detail': "No pots eliminar el teu propi rol d'administrador."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = UpdateUsuariSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info('Usuari actualitzat: user_id=%s admin_id=%s', pk, request.user.pk)
        return Response(UsuariSerializer(serializer.instance).data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        is_active = request.data.get('is_active')
        if is_active is not None:
            if not is_active and request.user.pk == pk:
                return Response(
                    {'detail': 'No pots deshabilitar el teu propi compte.'},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user.is_active = bool(is_active)
            user.save(update_fields=['is_active'])
            logger.info('Canvi is_active: user_id=%s is_active=%s admin_id=%s', pk, is_active, request.user.pk)
        return Response(UsuariSerializer(user).data)

    def delete(self, request, pk):
        if request.user.pk == pk:
            return Response(
                {'detail': 'No pots eliminar el teu propi compte.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        user = self.get_object(pk)
        if user.is_active:
            return Response(
                {'detail': "Has de deshabilitar l'usuari abans d'eliminar-lo."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logger.info('Usuari eliminat: user_id=%s admin_id=%s', pk, request.user.pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InfoImmobiliariaListCreateView(generics.ListCreateAPIView):
    queryset           = InfoImmobiliaria.objects.all()
    serializer_class   = InfoImmobiliariaSerializer


class InfoImmobiliariaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = InfoImmobiliaria.objects.all()
    serializer_class   = InfoImmobiliariaSerializer
