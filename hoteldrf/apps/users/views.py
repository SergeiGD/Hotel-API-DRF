from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import LoginSerializer, RefreshSerializer


class LoginAPIView(generics.GenericAPIView):
    """
    Вью для аутентификации
    """
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RefreshAPIView(generics.GenericAPIView):
    """
    Вью для обновления токена
    """
    serializer_class = RefreshSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
