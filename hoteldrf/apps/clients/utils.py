from django.http import Http404
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse

from ..users.utils import AuthUtil
from ..clients.models import Client
from ..orders.models import Order, Purchase
from .serializers import GuestSerializer


class SendVerifyEmailMixin:
    def send_verify_email(self, client, domain):

        token = RefreshToken.for_user(client).access_token

        relative_url = reverse('verify_registration')
        absolute_url = f'http://{domain}{relative_url}?token={str(token)}'
        email_body = f'Добрый день, {client.get_full_name()}! Для подтверждения регистрации перейдите по ссылке ниже: \n {absolute_url}'

        email_data = {
            'email_subject': 'Подтвердите регистрацию',
            'email_body': email_body,
            'email_to': client.email
        }

        AuthUtil.send_email(email_data)


class IsActiveUser(BasePermission):
    """
    Доступ только активным авторизированным пользователям (не гостям)
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active)


class ClientMixin:
    """
    Миксин для работы с авторизированным пользователям
    """
    permission_classes = (IsActiveUser, )

    def get_client(self):

        """
        Получение клиента
        """
        return get_object_or_404(Client, pk=self.request.user.pk)


class CartMixin:
    """
    Миксин для работы с корзиной клиента
    """

    def get_cart(self):
        """
        Получение корзины
        """
        # берем идентификатор корзины из почты
        if 'cart_uuid' in self.request.headers:
            cart = get_object_or_404(Order, cart_uuid=self.request.headers['cart_uuid'])
            if cart.is_cart:
                return cart

        raise Http404

    def confirm_cart(self):
        """
        Подтверждение корзины (коризу преващаем в подтвержденный заказ)
        """
        cart = self.get_cart()
        if self.request.user.is_authenticated:
            # если пользователь авторизирован, то в качестве клиента используется он
            cart.client = self.request.user
        else:
            # иначе берем данные из указанной почты
            serializer = GuestSerializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)

            # если клиент с такой почтой существует, то создаем заказ
            client = Client.objects.filter(email=serializer.validated_data['email']).first()
            if client:
                cart.client = client
            else:
                # иначе создаем клиента-гостя (active false, без пароля) из переданного email
                cart.client = serializer.save()

        # убираем идентификатор корзины
        cart.cart_uuid = None

        return cart


class ClientOrdersMixin(ClientMixin):
    """
    Миксин для работы с заказами клиента
    """

    def get_orders(self):
        client = self.get_client()
        return client.get_orders()

    def get_order(self, pk):
        return get_object_or_404(
            Order,
            id=pk,
            client=self.get_client()
        )

    def get_purchase(self, order_id, purchase_id):
        return get_object_or_404(
            Purchase,
            id=purchase_id,
            order__client_id=self.get_client().pk,
            order_id=order_id
        )
