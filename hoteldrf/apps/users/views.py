from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str, smart_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import AuthUtil
from .serializers import LoginSerializer, RefreshSerializer, RequestPasswordResetSerializer, SetNewPasswordSerializer
from .models import CustomUser


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


class RequestResetPasswordAPIView(APIView):
    """
    Вью для запроса сброса пароля
    """
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        user = CusomUser.objects.get(email=user_data['email'])
        # кодируем id пользователя
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        # генерируем токен сброса пароля
        token = PasswordResetTokenGenerator().make_token(user)
        # формируем часть url с параметрами
        relative_url = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
        domain = get_current_site(request).domain
        # формируем полный url
        absolute_url = f'http://{domain}{relative_url}'
        email_body = f'Добрый день! Для сброса пароля перейдите по ссылке ниже: \n {absolute_url}'

        email_data = {
            'email_subject': 'Смена пароля',
            'email_body': email_body,
            'email_to': user.email
        }

        # отправляем письмо на почту
        AuthUtil.send_email(email_data)
        return Response({
            'success': 'На почту отправлено письмо для подтверждения смены пароля'
        })


class PasswordTokenCheckAPIView(APIView):
    """
    Вью для установки нового пароля
    """
    def patch(self, request, uidb64, token):
        try:
            # пытаемся получить пользователя из закодированного id'шника в ссылке (uidb64)
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)
        except:
            return Response({
                'error': 'Эта ссылка не действительна'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # проверяем корректность токена сброса пароля
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({
                'error': 'Эта ссылка больше не действительна'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # меняем пароль
        serializer = SetNewPasswordSerializer(data=request.data, instance=user)
        serializer.is_valid()
        serializer.save()
        return Response({
            'success': 'Пароль успешно изменен'
        })
