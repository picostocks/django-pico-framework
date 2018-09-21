from rest_framework import serializers
from pico_framework.models import CurrentMarketPrice


class CurrentMarketPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentMarketPrice
        fields = '__all__'
