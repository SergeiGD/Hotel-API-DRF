from rest_framework.response import Response
from rest_framework import generics, status, viewsets
from django.contrib.sites.shortcuts import get_current_site
import jwt

from .serializers import RegisterSerializer, ClientsSerializer
from .models import Client
from django.conf import settings
from .utils import SendVerifyEmailMixin


class RegisterAPIView(SendVerifyEmailMixin, generics.GenericAPIView):
    """
    Вью для регистрации клиентов
    """
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        client_data = serializer.data

        client = Client.objects.get(email=client_data['email'])

        # отправляем письмо с подтверждением регистрации
        self.send_verify_email(client=client, domain=get_current_site(request).domain)

        return Response(client_data, status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(SendVerifyEmailMixin, generics.GenericAPIView):
    """
    Вью для подтверждения регистрации
    """
    def get(self, request):
        token = request.GET.get('token')
        try:
            # декодим токен
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            # получаем id клиента из мета-информации в токене
            client = Client.objects.get(id=payload['user_id'])
            if not client.is_active and not client.is_staff:
                # подтверждаем активацию аккаунта
                client.is_active = True
                client.save()
                return Response({
                    'email': 'Регастрация успешно подтвеждена'
                }, status=status.HTTP_200_OK)

            return Response({
                'email': 'Невозможно подтврдить регистрацию, похоже, аккаунт и так подветжден'
            }, status=status.HTTP_400_BAD_REQUEST)

        except jwt.ExpiredSignatureError:
            # если время жизни токена истекло, то декодим без проверки ошибки и отправляем письмо повторно
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256', options={"verify_signature": False})
            client = Client.objects.get(id=payload['user_id'])

            self.send_verify_email(client=client, domain=get_current_site(request).domain)

            return Response({
                'email': 'Невозможно подтврдить регистрацию, время подтверждения истекло, отправлено новое подтверждение'
            }, status=status.HTTP_400_BAD_REQUEST)

        except jwt.DecodeError:
            return Response({
                'email': 'Невозможно подтврдить регистрацию, проверьте корректность ссылки'
            }, status=status.HTTP_400_BAD_REQUEST)


class ClientsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с клиентами
    """
    queryset = Client.objects.all()
    serializer_class = ClientsSerializer

    def get_queryset(self):
        return Client.objects.filter(date_deleted=None, is_staff=False)

    def perform_destroy(self, instance):
        # переопределяем destroy, чтоб он просто почемал как удаленный, а не удалял реально
        instance = self.get_object()
        instance.mark_as_deleted()
