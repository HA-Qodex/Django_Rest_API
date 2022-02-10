from django.urls import path
from .views import *
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('products/', ProductView.as_view()),
    path('favourite/', FavouriteView.as_view()),
    path('cart/', CartView.as_view()),
    path('order/', OrderView.as_view()),
    path('login/', obtain_auth_token),
    path('registration/', RegisterView.as_view()),
    path('addtocart/', AddToCartView.as_view()),
    path('deleteProduct/', DeleteCartProduct.as_view()),
]
