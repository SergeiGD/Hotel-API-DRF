from rest_framework import serializers
from django.contrib.auth.models import Group

from .models import Worker, WorkerTimetable
from ..users.serializers import GroupsSerializer


class WorkersSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для оторабражения, создания, изменений сотрудников
    """
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = Worker
        fields = ['id', 'email', 'first_name', 'last_name', 'additional_info', 'salary']

    def create(self, validated_data):
        """
        Переопдереленный метод create, для вызова create_user + установки is_staff = True
        """
        data = {
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'additional_info': validated_data.get('additional_info'),
            'salary': validated_data['salary'],
            'is_staff': True
        }
        return Worker.objects.create(**data)


class WorkerTimetableSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для расписаний сотрудников
    """
    class Meta:
        model = WorkerTimetable
        exclude = ['worker', ]

    def validate(self, data):
        if 'start' in data:
            start = data['start']
            if self.partial and 'end' not in data:
                end = self.instance.end
            else:
                end = data['end']

            if start >= end:
                raise serializers.ValidationError({
                    'start': 'Начало должно быть меньше конца'
                })

        if 'end' in data:
            end = data['end']
            if self.partial and 'start' not in data:
                start = self.instance.end
            else:
                start = data['start']

            if start >= end:
                raise serializers.ValidationError({
                    'start': 'Начало должно быть меньше конца'
                })

        return data


class WorkerGroupsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для групп сотрудника
    """
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Group
        fields = ['groups']

    def update(self, instance, validated_data):
        instance.groups.add(validated_data['groups'])
        return instance

    @property
    def data(self):
        """
        Переопределенное св-во дата для сериализации groups
        """
        return GroupsSerializer(self.validated_data['groups']).data
