from django.shortcuts import render
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class ProductView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        query = Product.objects.all()
        serializer = ProductSerializer(query, many=True)
        return Response(serializer.data)


class FavouriteView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def post(self, request):
        data = request.data['id']
        try:
            product_obj = Product.objects.get(id=data)
            user = request.user
            single_favourite_product = Favourite.objects.filter(user=user).filter(product=product_obj).first()
            if single_favourite_product:
                check_favourite = single_favourite_product.isFavourite
                single_favourite_product.isFavourite = not check_favourite
                single_favourite_product.save()
            else:
                Favourite.objects.create(product=product_obj, user=user, isFavourite=True)
            response_message = {'error': False}
        except:
            response_message = {'error': True}
        return Response(response_message)
