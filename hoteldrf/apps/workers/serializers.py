from rest_framework import serializers

from .models import Worker


class WorkersSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для оторабражения, создания, изменений сотрудников
    """

    class Meta:
        model = Worker
        fields = ['id', 'email', 'first_name', 'last_name', 'additional_info']

    def create(self, validated_data):
        """
        Переопдереленный метод create, для вызова create_user + установки is_staff = True
        """
        data = {
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'additional_info': validated_data['additional_info'],
            'is_staff': True,
        }
        return Worker.objects.create_user(**data)
