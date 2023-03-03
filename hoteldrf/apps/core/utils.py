import uuid

from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


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


