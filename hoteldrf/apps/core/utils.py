import uuid


def build_photo_path(instance, filename):
    """
    генерация пути для фотографий
    """
    ext = filename.split('.')[-1]
    code = uuid.uuid4()
    return '{0}.{1}'.format(code, ext)
