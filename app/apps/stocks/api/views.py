from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from .serializers import CandleSerializer, StockSerializer
from ..models import Candle, Stock


class CandleListAPIView(ListAPIView):
    serializer_class = CandleSerializer

    def get_queryset(self):
        ticker = self.kwargs['ticker']
        return Candle.objects.filter(stock__ticker=ticker)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({'message': 'Candles not found for this stock'}, status=status.HTTP_404_NOT_FOUND)
        
        all_param = self.request.query_params.get('all')
        if all_param and all_param.lower() == 'true':
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            count = len(data)
            return Response({'count': count, 'next': None, 'previous': None, 'results': data})
        
        return super().list(request, *args, **kwargs)


class StockDetailAPIView(RetrieveAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    lookup_field = 'ticker'
    lookup_url_kwarg = 'ticker'
