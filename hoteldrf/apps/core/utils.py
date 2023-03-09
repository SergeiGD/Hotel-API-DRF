import uuid

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.utils.decorators import classonlymethod


def idempotency_key_marker(class_view):
    """
    Декоратор для метода as_view для отметки view, как требующего проверки ключа идемпотентности
    """
    orig_as_view = class_view.as_view

    @classonlymethod
    def as_view(cls, *args, **kwargs):
        # вызываем as_view у класса, к которому будет применен декоратор и получаем view
        view = orig_as_view(*args, **kwargs)
        # устанавливаем флаг
        view.idempotency_key = True
        return view

    class_view.as_view = as_view
    return class_view


def idempotency_key_decorator(func_view):
    """
    Декоратор для func based view, для отметки view, как требующего проверки ключа идемпотентности
    """
    func_view.idempotency_key = True
    return func_view


def build_photo_path(instance, filename):
    """
    генерация пути для фотографий
    """
    ext = filename.split('.')[-1]
    code = uuid.uuid4()
    return '{0}.{1}'.format(code, ext)


def check_uuid(value):
    """
    Проверка валидности uuid ключа
    """
    try:
        uuid.UUID(str(value), version=4)
        return True
    except ValueError:
        return False


def gen_middleware_response(msg, status):
    """
    Установка доп. параметров ответа
    """
    response = Response(msg, status=status)
    response.accepted_renderer = JSONRenderer()
    response.accepted_media_type = "application/json"
    response.renderer_context = {}
    response.render()
    return response


