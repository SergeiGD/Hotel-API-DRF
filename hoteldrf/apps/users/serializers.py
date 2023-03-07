from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import Group, Permission

from .models import CustomUser


class LoginSerializer(serializers.Serializer):
    """
    Кастомный сериализатор для аутентификации (написан свой сугубо в ознакомительных целях)
    """
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get('email', '')
        password = data.get('password', '')

        # пробуем аутетифицировать пользователя по данным эл. почты и пароля
        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
            raise AuthenticationFailed('Не найден активный пользователь с таким логином и паролем')

        return {
            'access': user.get_tokens()['access'],
            'refresh': user.get_tokens()['refresh'],
        }


class RefreshSerializer(serializers.Serializer):
    """
    Кастомный сериализатор для обновления токена (написан свой сугубо в ознакомительных целях)
    """
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)

    def validate(self, data):


        # проверяем, не находится ли токен в черном списке
        try:
            refresh = RefreshToken(data.get('refresh', ''))
        except TokenError:
            raise serializers.ValidationError({
                    'refresh': 'Этот токен не действителен'
                })

        # если выставлена настройка обновления рефреш токена при запросе
        if api_settings.ROTATE_REFRESH_TOKENS:
            # если выставлена настройка добавления токена в черный список при использовании
            if api_settings.BLACKLIST_AFTER_ROTATION:
                refresh.blacklist()

            # устанавливаем новый токен и время жизни
            refresh.set_jti()
            refresh.set_exp()

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True)

    def save(self, **kwargs):
        try:
            RefreshToken(self.validated_data['refresh']).blacklist()

        except TokenError:
            raise serializers.ValidationError({
                'refresh': 'Этот токен не действителен'
            })

        return self.instance


class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Сериалайзер для запроса смены пароля
    """
    email = serializers.EmailField(required=True)

    def validate(self, data):
        # если ли активный пользователь с указанной почтой
        if not CustomUser.objects.filter(
            email=data['email'],
            is_active=True
        ).exists():
            raise serializers.ValidationError({
                'email': '  Не найден активный пользователь с таким адресом эл. почты'
            })

        return data


class SetNewPasswordSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для установки установки новго пароля
    """
    password1 = serializers.CharField(min_length=6, write_only=True, required=True)
    password2 = serializers.CharField(min_length=6, write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Пароли не совпадают'
            })

        return super().validate(data)

    def update(self, instance, validated_data):
        # переопределяем update для установки пароля
        instance.set_password(validated_data['password1'])
        instance.save()
        return instance


class GroupsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для групп
    """
    class Meta:
        model = Group
        fields = ['name', 'id']


class PermissionsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для разрешений
    """
    class Meta:
        model = Permission
        fields = '__all__'


class GroupPermissionsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для разрешений группы
    """
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all())

    class Meta:
        model = Group
        fields = ['permissions']

    def update(self, instance, validated_data):
        instance.permissions.add(validated_data['permissions'])
        return instance

    @property
    def data(self):
        """
        Переопределенное св-во дата для сериализации permissions
        """
        return PermissionsSerializer(self.validated_data['permissions']).data
