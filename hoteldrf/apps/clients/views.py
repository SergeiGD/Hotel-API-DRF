from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import smart_str, smart_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser
from rest_framework.response import Response
from rest_framework import generics, status, viewsets
from django.contrib.sites.shortcuts import get_current_site
import jwt
from rest_framework.views import APIView

from .serializers import RegisterSerializer, ClientsSerializer, CartSerializer, \
                        ClientOrdersSerializer, ClientPurchasesSerializer, ClientProfileSerializer
from .models import Client
from django.conf import settings
from .utils import SendVerifyEmailMixin
from ..orders.models import Purchase, Order, Cart
from ..orders.mixins import PurchaseManageMixin, PurchaseCreateMixin
from .utils import CartMixin, ClientOrdersMixin, ClientMixin
from ..core.permissions import FullModelPermissionsPermissions


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

        return Response({
            'success': 'На почту отправлено письмо для подтверждения регистрации'
        }, status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(SendVerifyEmailMixin, generics.GenericAPIView):
    """
    Вью для подтверждения регистрации
    """
    def get(self, request):
        # TODO мб параметр переделать в прям часть ссылки как при сбросе пароля
        token = request.GET.get('token')
        try:
            # декодим токен
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            # получаем id клиента из мета-информации в токене
            client = Client.objects.get(id=payload['user_id'])
            if not client.is_active:
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

            if client.is_active:
                return Response({
                    'email': 'Невозможно подтврдить регистрацию, похоже, аккаунт и так подветжден'
                }, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = (IsAdminUser, FullModelPermissionsPermissions, )
    queryset = Client.objects.all()
    serializer_class = ClientsSerializer
    # убираем метод delete, т.к. вообще не удаляем клиентов
    http_method_names = ['get', 'post', 'put', 'patch',  'head', 'options']

    def get_queryset(self):
        return Client.objects.all()


class CartRetrieveAPIView(CartMixin, APIView):
    """
    Вью для получения и создания коризны
    """

    def get(self, request):
        serializer = CartSerializer(self.get_cart())
        return Response(serializer.data)

    def post(self, request):
        cart = Cart.objects.create()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartPurchasesCreateAPIView(CartMixin, PurchaseCreateMixin, APIView):
    """
    Вью для добавления покупок в корзину
    """
    def get_order(self):
        return self.get_cart()


class CartPurchasesManageAPIView(PurchaseManageMixin, CartMixin, APIView):
    """
    Вью для управления покупками в корзине
    """
    def get_object(self):
        return get_object_or_404(Purchase, pk=self.kwargs['purchase_id'], order=self.get_cart())


class CartPayPrepaymentAPIView(CartMixin, APIView):
    """
    Вью для внесения предоплаты за корзину
    """
    def patch(self, request):
        order = self.confirm_cart()
        order.mark_as_prepayment_paid()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartPayAPIView(CartMixin, APIView):
    """
    Вью для оплаты корзины
    """
    def patch(self, request):
        order = self.confirm_cart()
        order.mark_as_paid()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientOrdersListAPIView(ClientOrdersMixin, generics.ListAPIView):
    """
    Вью для получения заказов клиента
    """
    serializer_class = ClientOrdersSerializer

    def get_queryset(self):
        return self.get_orders()


class ClientOrderManageAPIView(ClientOrdersMixin, APIView):
    """
    Вью для управления заказом клиента
    """
    def get_object(self):
        return self.get_order(self.kwargs['pk'])

    def get(self, request, pk):
        serializer = ClientOrdersSerializer(self.get_object())
        return Response(serializer.data)

    def delete(self, request, pk):
        # не удаляем, а отмечаем как отмененный
        self.get_object().mark_as_canceled()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientPurchasesListAPIView(ClientOrdersMixin, APIView):
    """
    Вью для получения списка покупок заказа клиента
    """
    def get_object(self):
        return self.get_order(self.kwargs['pk'])

    def get(self, request, pk):
        serializer = ClientPurchasesSerializer(self.get_object().purchases.all(), many=True)
        return Response(serializer.data)


class ClientPurchaseManageAPIView(PurchaseManageMixin, ClientOrdersMixin, APIView):
    """
    Вью для управления покупками в заказе клиента
    """
    def get_object(self):
        return self.get_purchase(
            order_id=self.kwargs['pk'],
            purchase_id=self.kwargs['purchase_id']
        )


class ClientOrderPayAPIView(ClientOrdersMixin, APIView):
    """
    Вью для полной оплаты заказы клиента
    """
    def patch(self, request):
        order = self.get_order(self.kwargs['pk'])
        order.mark_as_paid()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientProfileInfo(ClientMixin, generics.RetrieveUpdateAPIView):
    """
    Вью для просмотра и изменения профиля клиента
    """
    serializer_class = ClientProfileSerializer

    def get_object(self):
        return self.get_client()



