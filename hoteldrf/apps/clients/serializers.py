from rest_framework import serializers
from .models import Client


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для регистрации клиентов
    """
    password1 = serializers.CharField(min_length=6, write_only=True)
    password2 = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = Client
        fields = ['id', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Пароли не совпадают'
            })

        return super().validate(data)

    def create(self, validated_data):
        """
        Переопдереленный метод create, для вызова create_user, установки is_staff = False и пароля
        """
        data = {
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'password': validated_data['password1'],
            'is_staff': False,
            'is_active': False
        }
        return Client.objects.create_user(**data)


class ClientsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для оторабражения, создания, изменений клиентов
    """
    email = serializers.EmailField(read_only=True)
    orders_count = serializers.ReadOnlyField()
    money_spent = serializers.ReadOnlyField()

    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'additional_info', 'orders_count', 'money_spent', 'email']

    def create(self, validated_data):
        """
        Переопдереленный метод create, для вызова create_user + установки is_staff и is_active False
        """
        data = {
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'additional_info': validated_data['additional_info'],
            'is_staff': False,
            'is_active': False
        }
        return Client.objects.create_user(**data)
