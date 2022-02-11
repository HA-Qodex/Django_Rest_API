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
            response_message = {
                "success": True,
                "message": "",
                "data": data,
                "error": "",
                "error_code": 200}
        except:
            response_message = {
                "success": False,
                "message": "Something wrong...",
                "data": "",
                "error": "",
                "error_code": 400}
        return Response(response_message)


class OrderView(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TokenAuthentication, ]

    def get(self, request):
        try:
            query = Order.objects.filter(cart__user=request.user)
            serializer = OrderSerializer(query, many=True)
            response_message = {"error": False, "data": serializer.data}
        except:
            response_message = {"error": True, "data": "No Data"}
        return Response(response_message)


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        product_id = request.data["id"]
        product_obj = Product.objects.get(id=product_id)
        cart = Cart.objects.filter(user=request.user).filter(isComplete=False).first()
        cart_product_obj = CartProduct.objects.filter(product__id=product_id).first()

        try:
            if cart:
                this_product_in_cart = cart.cartproduct_set.filter(product=product_obj)
                if this_product_in_cart.exists():
                    cart_product_uct = CartProduct.objects.filter(product=product_obj).filter(
                        cart__isComplete=False).first()
                    cart_product_uct.quantity += 1
                    cart_product_uct.subtotal += product_obj.sellPrice
                    cart_product_uct.save()
                    cart.total += product_obj.sellPrice
                    cart.save()
                else:
                    cart_product_new = CartProduct.objects.create(
                        cart=cart,
                        price=product_obj.sellPrice,
                        quantity=1,
                        subtotal=product_obj.sellPrice
                    )
                    cart_product_new.product.add(product_obj)
                    cart.total += product_obj.sellPrice
                    cart.save()
            else:
                Cart.objects.create(user=request.user, total=0, isComplete=False)
                new_cart = Cart.objects.filter(user=request.user).filter(isComplete=False).first()
                cart_product_new = CartProduct.objects.create(
                    cart=new_cart,
                    price=product_obj.sellPrice,
                    quantity=1,
                    subtotal=product_obj.sellPrice
                )
                cart_product_new.product.add(product_obj)
                new_cart.total += product_obj.sellPrice
                new_cart.save()
            response_message = {
                "success": True,
                "message": "Product added to cart",
                "data": "",
                "error": "",
                "error_code": 200
            }
        except:
            response_message = {
                "success": False,
                "message": "Product failed to add in cart",
                "data": "",
                "error": "",
                "error_code": 400
            }
        return Response(response_message)


class DeleteCartProductView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_product_id = request.data["id"]
        try:
            cart_product_obj = CartProduct.objects.get(id=cart_product_id)
            cart = Cart.objects.filter(user=request.user).filter(isComplete=False).first()
            cart.total -= cart_product_obj.subtotal
            cart_product_obj.delete()
            cart.save()
            response_message = {
                "success": True,
                "message": "Product deleted successfully",
                "data": "",
                "error": "",
                "error_code": 200
            }
        except:
            response_message = {
                "success": False,
                "message": "Product delete failed",
                "data": "",
                "error": "",
                "error_code": 400
            }
        return Response(response_message)


class DeleteCartView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        cart_id = request.data["id"]
        try:
            cart_obj = Cart.objects.get(id=cart_id)
            cart_obj.delete()
            response_message = {
                "success": True,
                "message": "Cart has been deleted",
                "data": "",
                "error": "",
                "error_code": 200
            }
        except:
            response_message = {
                "success": False,
                "message": "Cart delete failed",
                "data": "",
                "error": "",
                "error_code": 400
            }
        return Response(response_message)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):

        try:
            data = request.data
            cart_id = data['cart_id']
            address = data['address']
            email = data['email']
            phone = data['phone']
            cart_obj = Cart.objects.get(id=cart_id)
            cart_obj.isComplete = True
            cart_obj.save()
            Order.objects.create(
                cart=cart_obj,
                email=email,
                address=address,
                phone=phone
            )
            response_message = {
                "success": True,
                "message": "Order has been created successfully",
                "data": "",
                "error": "",
                "error_code": 200
            }
        except:
            response_message = {
                "success": False,
                "message": "Order Creation failed",
                "data": "",
                "error": "",
                "error_code": 400
            }
        return Response(response_message)
