from rest_framework import serializers
from pico_framework import models
from pico_framework import utils


class StatsMarketPriceSerializer(serializers.ModelSerializer):
    market = serializers.SerializerMethodField()
    stock_code = serializers.SerializerMethodField()
    unit_code = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = models.StatsMarketPrice
        fields = '__all__'

    def get_market(self, obj):
        return "%s/%s" %(obj.get_stock_id_display(), obj.get_unit_id_display())

    def get_stock_code(self, obj):
        return obj.get_stock_id_display()

    def get_unit_code(self, obj):
        return obj.get_unit_id_display()

    def get_price(self, obj):
        return "{:.5f}".format(obj.price)


class CurrentMarketPriceSerializer(StatsMarketPriceSerializer):
    change = serializers.SerializerMethodField()

    def get_change(self, obj):
        change = utils.get_change(obj.stock_id, obj.unit_id)
        if not change:
            return 0

        # To eliminate "-0.00"
        change = float("{:.2f}".format(change))
        return "{:.2f}".format(change)
