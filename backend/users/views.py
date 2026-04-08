from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Usuari, Propietari
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UsuariSerializer,
    PropietariSerializer,
)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UsuariSerializer(user).data,
        })


class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UsuariSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request):
        return Response(UsuariSerializer(request.user).data)


class PropietariListCreateView(generics.ListCreateAPIView):
    queryset = Propietari.objects.all()
    serializer_class = PropietariSerializer


class PropietariDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Propietari.objects.all()
    serializer_class = PropietariSerializer
