from pico_framework import consts
from pico_framework import models
from pico_framework import utils
from rest_framework import serializers


class StatsMarketPriceSerializer(serializers.ModelSerializer):
    market = serializers.SerializerMethodField()
    stock_code = serializers.SerializerMethodField()
    unit_code = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    added = serializers.SerializerMethodField()

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
        return utils.num2str(obj.price, consts.MAX_PRICE_DIGITS)

    def get_added(self, obj):
        return obj.timestamp


class CurrentMarketPriceSerializer(StatsMarketPriceSerializer):
    change = serializers.SerializerMethodField()

    def get_change(self, obj):
        change = utils.get_change(obj.stock_id, obj.unit_id)
        if not change:
            return 0

        # To eliminate "-0.00"
        change = float("{:.2f}".format(change))
        if not change:
            return 0

        return "{:.2f}".format(change)
