from django.contrib.auth import logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str, smart_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import generics, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import Group, Permission

from .utils import AuthUtil
from .serializers import LoginSerializer, RefreshSerializer, RequestPasswordResetSerializer, SetNewPasswordSerializer,\
                        LogoutSerializer, GroupsSerializer, PermissionsSerializer, GroupPermissionsSerializer
from .models import CustomUser
from ..core.permissions import FullModelPermissionsPermissions


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


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RequestResetPasswordAPIView(APIView):
    """
    Вью для запроса сброса пароля
    """
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data
        user = CustomUser.objects.get(email=user_data['email'])
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': 'Пароль успешно изменен'
        })


class GroupsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с группами
    """
    queryset = Group.objects.all()
    serializer_class = GroupsSerializer
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions)


class PermissionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для работы с правами
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionsSerializer
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions)


class RolePermissionsListAPIView(APIView):
    """
    Вью для получения списка и добавления прав к роли
    """
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions)

    def get_queryset(self):
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        return group.permissions.all()

    def get(self, request, pk):
        serializer = PermissionsSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        serializer = GroupPermissionsSerializer(data=request.data, instance=group)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RolePermissionDeleteAPIView(APIView):
    """
    Вью для удаление разрешения у группы
    """
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions)

    def get_queryset(self):
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        return group.permissions.all()

    def delete(self, request, permission_id, pk):
        group = get_object_or_404(Group, pk=pk)
        permission = get_object_or_404(Permission, pk=permission_id)
        group.permissions.remove(permission)
        return Response(status=status.HTTP_204_NO_CONTENT)
