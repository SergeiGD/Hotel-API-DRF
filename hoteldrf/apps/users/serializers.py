from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings


class LoginSerializer(serializers.Serializer):
    """
    Кастомный сериализатор для аутентификации (написан своя сугубо в учебных целях)
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
    Кастомный сериализатор для обновления токена (написана своя сугубо в учебных целях)
    """
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)

    def validate(self, data):

        # проверяем, не находится ли токен в черном списке
        try:
            refresh = RefreshToken(data.get('refresh', ''))
        except TokenError:
            raise serializers.ValidationError({
                    'refresh': 'Этот токен больше не действителен'
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

