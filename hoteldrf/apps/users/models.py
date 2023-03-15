from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    # TODO: номер телефона

    username = None
    email = models.EmailField(
        verbose_name='Эл. почта',
        unique=True
    )
    additional_info = models.JSONField(
        verbose_name='Доп. информация',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ['last_name']

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

