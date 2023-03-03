import uuid

from django.http import HttpResponseForbidden
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import generics, status

from .models import IdempotencyKey
from .utils import check_uuid, gen_middleware_response


def idempotency_key_middleware(get_response):
    """
    Middleware для работы с ключем индепотености для POST запросов
    """

    def middleware(request):
        if request.method == 'POST':
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

        response = get_response(request)

        # при успешном POST запросе добавляем ключ в таблицу использованных ключей
        if request.method == 'POST' and status.is_success(response.status_code):
            idempotency_key = request.headers['Idempotency-Key']
            IdempotencyKey.objects.create(id=idempotency_key)

        return response

    return middleware
