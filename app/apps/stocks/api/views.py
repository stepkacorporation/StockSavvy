from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CandleSerializer, StockSerializer, FavouriteSerializer
from ..models import Candle, Stock, Favourite


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


class AddOrRemoveFavouriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FavouriteSerializer(data=request.data)
        if serializer.is_valid():
            stock = serializer.validated_data['stock']
            user = serializer.validated_data['user']

            if user != request.user:
                return Response(
                    {'error': 'You can add favorites only for your account.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            try:
                favourite = Favourite.objects.get(user=user, stock=stock)
                favourite.delete()
                return Response(
                    {'message': f'"{stock.shortname}" - removed from favourites.'},
                    status=status.HTTP_200_OK
                )
            except Favourite.DoesNotExist:
                serializer.save()
                return Response(
                    {'message': f'"{stock.shortname}" - added to favourites.'},
                    status=status.HTTP_201_CREATED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
