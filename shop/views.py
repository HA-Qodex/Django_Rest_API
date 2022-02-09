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


class RegisterView(APIView):
    def post(self, request):
        serializers = UserSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({"error": serializers.default_error_messages})
        return Response({"error": serializers.errors})


class CartView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        user = request.user
        try:
            cart_obj = Cart.objects.filter(user=user).filter(isComplete=False)
            data = []
            cart_serializer = CartSerializer(cart_obj, many=True)
            for cart in cart_serializer.data:
                cart_product_obj = CartProduct.objects.filter(cart=cart["id"])
                cart_product_obj_serializer = CartProductSerializer(cart_product_obj, many=True)
                cart['cartProducts'] = cart_product_obj_serializer.data
                data.append(cart)
            response_message = {"error": False, "data": data}
        except:
            response_message = {"error": False, "data": "No Data"}
        return Response(response_message)


class OrderView(APIView):
    permission_classes = [IsAuthenticated,]
    authentication_classes = [TokenAuthentication,]

    def get(self, request):
        try:
            query = Order.objects.filter(cart__user=request.user)
            serializer = OrderSerializer(query, many=True)
            response_message = {"error": False, "data": serializer.data}
        except:
            response_message = {"error": True, "data": "No Data"}
        return Response(response_message)
