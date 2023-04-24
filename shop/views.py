""" app.shop views. """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.response import Response

from cart.serializers import QuantitySerializer
from shop.filterset import ProductFilter
from shop.models import Category, Product
from shop.serializers import CategoryDetailSerializer, CategorySerializer, ProductDetailSerializer, \
    ProductListSerializer
from shop.services import add_cart


# Create your views here

class CategoryListView(generics.ListAPIView):
    """ Category list. """
    queryset = Category.objects.filter(level=0)
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveAPIView):
    """ Category detail. """
    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategoryDetailSerializer


class ProductListView(generics.ListAPIView):
    """ Products list. """
    queryset = Product.objects.select_related('category').prefetch_related('images')
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductDetailView(generics.RetrieveAPIView, generics.CreateAPIView):
    """ Product detail. """
    queryset = Product.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        """ Choice serializer. """
        dict_method = {
            'POST': QuantitySerializer,
            'GET': ProductDetailSerializer
            }
        return dict_method[self.request.method]

    def post(self, request, *args, **kwargs):
        """ Adds product to cart. Takes quantity from POST request."""
        serializer = QuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.get_object()
        quantity = int(serializer.validated_data['quantity'])
        return_response = add_cart(request, product=product, quantity=quantity)
        dict_response = {
            None: Response(data=f"{product} add to cart", status=status.HTTP_201_CREATED),
            'not found': Response(data=f"Product {product} not found.", status=status.HTTP_404_NOT_FOUND),
            'many quantity': Response(f"Quantity more {product.quantity} product in stock.",
                                      status=status.HTTP_400_BAD_REQUEST),
            }
        return dict_response[return_response]
