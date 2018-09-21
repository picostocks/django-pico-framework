from rest_framework import serializers
from pico_framework.models import CurrentMarketPrice


class CurrentMarketPriceSerializer(serializers.ModelSerializer):
    market = serializers.SerializerMethodField()
    stock_code = serializers.SerializerMethodField()
    unit_code = serializers.SerializerMethodField()

    class Meta:
        model = CurrentMarketPrice
        fields = '__all__'

    def get_market(self, obj):
        return "%s/%s" %(obj.get_stock_id_display(), obj.get_unit_id_display())

    def get_stock_code(self, obj):
        return obj.get_stock_id_display()

    def get_unit_code(self):
        return obj.get_unit_id_display()
