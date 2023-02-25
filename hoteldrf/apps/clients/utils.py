from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from .models import Client
from ..users.utils import AuthUtil


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
