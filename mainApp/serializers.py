from django.core import serializers
from rest_framework.serializers import ModelSerializer
from .models import Rover, Session


class RoverSerializer(ModelSerializer):
    class Meta:
        model = Rover
        fields = '__all__'


class SessionSerializer(ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


