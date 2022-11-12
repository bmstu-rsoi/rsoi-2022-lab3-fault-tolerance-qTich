from rest_framework import serializers
from .models import ReservationModel


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationModel
        fields = "__all__"
