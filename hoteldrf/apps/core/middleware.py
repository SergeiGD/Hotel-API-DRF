from django.http import HttpResponseForbidden
from rest_framework.response import Response


def idempotency_key_middleware(get_response):

    def middleware(request):
        if request.method == 'POST' and 'Idempotency-Key' in request.headers:
            idempotency_key = request.headers['Idempotency-Key']
            # if idempotency_key in Keys.objcts.get...
            # ИЛИ МБ НЕ В middleware ЭТО ДЕЛАТЬ, А МИКСИН + ДЕКОРАТОР СДЕЛАТЬ ДЛЯ ЭТОГО

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware