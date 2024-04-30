from rest_framework import serializers

from ..models import Candle, Stock, Favourite


class CandleSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(source='time_range.lower', read_only=True)
    end_time = serializers.DateTimeField(source='time_range.upper', read_only=True)

    class Meta:
        model = Candle
        fields = ('open', 'close', 'high', 'low', 'value', 'volume', 'start_time', 'end_time')



class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = '__all__'
