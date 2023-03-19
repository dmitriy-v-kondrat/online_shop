
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response

from cart.cart import Cart
from cart.serializers import AddToCartSerializer
from shop.filterset import ProductFilter
from shop.models import Category, Product
from shop.serializers import ProductDetailSerializer, ProductListSerializer
from shop.services import add_cart

# Create your views here


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.select_related('category').prefetch_related('images')
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductDetailView(generics.RetrieveAPIView, generics.CreateAPIView):
    queryset = Product.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        dict_method = {
            'POST': AddToCartSerializer,
            'GET': ProductDetailSerializer
            }
        return dict_method[self.request.method]

    def post(self, request, *args, **kwargs):
        """ Add to cart. """
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = Cart(request)
        product = self.get_object()
        quantity = int(serializer.validated_data['quantity'])
        return_response = add_cart(cart=cart, product=product, quantity=quantity)
        dict_response = {
            None: Response(data=f"{product} add to cart", status=status.HTTP_201_CREATED),
            'not found': Response(data=f"Product {product} not found.", status=status.HTTP_404_NOT_FOUND),
            'many quantity': Response(f"Quantity more {product.quantity} product in stock.",
                                      status=status.HTTP_400_BAD_REQUEST),
            }
        return dict_response[return_response]
