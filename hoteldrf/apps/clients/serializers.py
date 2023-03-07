from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from .models import Client
from ..orders.models import Cart
from ..orders.serializers import PurchasesSerializer, OrdersSerializer, CreatePurchaseSerializer, EditPurchaseSerializer
from ..users.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для регистрации клиентов
    """
    password1 = serializers.CharField(min_length=6, write_only=True)
    password2 = serializers.CharField(min_length=6, write_only=True)
    email = serializers.EmailField(validators=[])

    class Meta:
        model = Client
        fields = ['id', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Пароли не совпадают'
            })

        if Client.objects.filter(email=data['email'], is_active=True).exists():
            raise serializers.ValidationError({
                'password': 'Уже существует активный пользователь с этой электронной почтой'
            })

        return super().validate(data)

    def create(self, validated_data):
        """
        Переопдереленный метод create, для вызова create_user, установки is_staff = False и пароля
        """
        data = {
            'email': validated_data['email'],
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
            'password': validated_data['password1'],
            'is_staff': False,
            'is_active': False
        }
        client = Client.objects.filter(email=data['email'], is_active=False).first()
        if client is not None:
            # если пользователь-гость (создавал заказы с указанным email и is_active=False) пытается зарегистироваться,
            # то просто обновляем данные
            client.first_name = data['first_name']
            client.last_name = data['last_name']
            client.save()
            client.set_password(data['password'])
            return client
        return Client.objects.create_user(**data)


class ClientsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для оторабражения, создания, изменений клиентов
    """
    orders_count = serializers.ReadOnlyField()
    money_spent = serializers.ReadOnlyField()

    class Meta:
        model = Client
        fields = ['id', 'first_name', 'last_name', 'additional_info', 'orders_count', 'money_spent', 'email']

    def create(self, validated_data):
        """
        Переопдереленный метод create, для установки is_staff и is_active False
        """
        data = {
            'email': validated_data['email'],
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
            'additional_info': validated_data.get('additional_info'),
            'is_staff': False,
            'is_active': False
        }
        return Client.objects.create(**data)


class ClientPurchasesSerializer(PurchasesSerializer):
    """
    Сериалайзер для покупок в клиента
    """
    class Meta(PurchasesSerializer.Meta):
        exclude = [
            *PurchasesSerializer.Meta.exclude,
            'is_paid',
            'is_prepayment_paid',
            'is_refund_made',
            'is_canceled',
            'refund',
            'prepayment'
        ]


class CartSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для корзины
    """
    prepayment = serializers.ReadOnlyField()
    price = serializers.ReadOnlyField()
    purchases = ClientPurchasesSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['price', 'prepayment', 'purchases', 'cart_uuid']


class GuestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = Client
        fields = ['email', ]

    def create(self, validated_data):
        """
        Переопдереленный метод create, для вызова create_user, установки is_staff и is_active False
        """
        data = {
            'email': validated_data['email'],
            'is_staff': False,
            'is_active': False
        }
        return Client.objects.create(**data)


class ClientOrdersSerializer(OrdersSerializer):
    """
    Сериалайзер для заказов клиента
    """
    class Meta(OrdersSerializer.Meta):
        exclude = [
            *OrdersSerializer.Meta.exclude,
            'client'
        ]


class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для профиля клиента
    """
    orders_count = serializers.ReadOnlyField()

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'orders_count']


