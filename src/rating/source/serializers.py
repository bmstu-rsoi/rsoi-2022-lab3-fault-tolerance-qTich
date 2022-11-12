from rest_framework import serializers
from .models import RatingModel


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingModel
        fields = ("stars",)
