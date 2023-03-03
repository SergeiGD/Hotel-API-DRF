import uuid

from django.db import models


class IdempotencyKey(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False
    )

    class Meta:
        indexes = [
            models.Index(fields=['date_created', ]),
        ]
