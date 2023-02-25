from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False, verbose_name='наименование')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

