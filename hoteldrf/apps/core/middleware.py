import uuid

from django.http import HttpResponseForbidden
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import generics, status

from .models import IdempotencyKey
from .utils import check_uuid, gen_middleware_response


class IdempotencyKeyMiddleware:

    def __init__(self, get_response):
        self.idempotency_key = None
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # при успешном POST запросе, если был использован ключ индепотентнти,
        # то добавляем его в таблицу использованных ключей
        if request.method == 'POST' and status.is_success(response.status_code) and self.idempotency_key is not None:
            IdempotencyKey.objects.create(id=self.idempotency_key)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        idempotency_key_required = getattr(view_func, 'idempotency_key', False)
        # если post запрос и было указано, что ключ нужен
        if idempotency_key_required and request.method == 'POST':
            # если нету ключа, то возвращем ошибку
            if 'Idempotency-Key' not in request.headers:
                return gen_middleware_response(
                    {'error': 'У запроса отсуствует ключ индепотености (заголовок Idempotency-Key)'},
                    status.HTTP_409_CONFLICT
                )

            idempotency_key = request.headers['Idempotency-Key']

            # проверка корректности фотрмата ключа
            if not check_uuid(idempotency_key):
                return gen_middleware_response(
                    {'error': 'Неверный формат ключа индепотености (необходим UUID4)'},
                    status.HTTP_409_CONFLICT
                )

            # если такой ключ уже был использовал, то возвращаем ошибку
            if IdempotencyKey.objects.filter(id=idempotency_key).exists():
                return gen_middleware_response(
                    {'error': 'Запрос с таким ключ уже был сделан'},
                    status.HTTP_409_CONFLICT
                )

            # фиксируем значения ключа, чтоб при успешном запросе пометить его как использованный
            self.idempotency_key = idempotency_key
