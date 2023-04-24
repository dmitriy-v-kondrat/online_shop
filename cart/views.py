""" app.cart views. """

from django.shortcuts import redirect
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from cart.cart import Cart
from cart.serializers import PaymentSerializer, QuantitySerializer
from cart.services import data_for_buyers, data_payment_pending, payment_detail, update_quantity_cart
from users.models import Buyer


class CartDetailAPI(APIView):
    """ Products in a cart. """
    def get(self, request):
        cart = Cart(request)
        return Response(data={'product': cart,
                              'total price': cart.get_total_price(),
                              }
                        )


class CartUpdateQuantityView(generics.UpdateAPIView):
    """ Update product quantity. """
    serializer_class = QuantitySerializer

    def update(self, request, *args, **kwargs):
        serializer = QuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_quantity_cart(request,
                             product_id=str(kwargs['pk']),
                             quantity=int(serializer.validated_data['quantity'])
                             )
        dict_response = {
            True: Response(data=f"product {str(kwargs['pk'])} update", status=status.HTTP_201_CREATED),
            False: Response(status=status.HTTP_400_BAD_REQUEST)
            }
        return dict_response[request.session.modified]


class CartDestroyProductView(APIView):
    """ Remove product from a cart. """
    def delete(self, request, pk):
        cart = Cart(request)
        cart.remove(pk=pk)
        dict_response = {
            True: Response(data=f"Product {pk} removed", status=status.HTTP_204_NO_CONTENT),
            False: Response(status=status.HTTP_400_BAD_REQUEST)
            }
        return dict_response[request.session.modified]


class ClearCartView(APIView):
    """ Clear cart. """
    def delete(self, request):
        cart = Cart(request)
        cart.clear()
        dict_response = {
            True: Response(data=f"Cart deleted", status=status.HTTP_204_NO_CONTENT),
            False: Response(status=status.HTTP_400_BAD_REQUEST)
            }
        return dict_response[request.session.modified]


class PaymentView(mixins.CreateModelMixin, generics.GenericAPIView):
    """ Takes buyer data for pay. """
    queryset = Buyer.objects.all()
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checkout_data = data_for_buyers(request, buyer=serializer.data)
        return Response(data={'Check data and correct if necessary': checkout_data,
                              'Pay yookassa': request.build_absolute_uri(reverse('redirect_to_pay'))
                              }
                        )


class RedirectToPayView(APIView):
    """ Sends for writing in db data buyer, products and payment. Redirect buyer on payment page."""

    def get(self, request, *args, **kwargs):
        data_payment_pending(request)
        return redirect(request.session['to_pay'])


class PaymentDetailAPI(APIView):
    """ Payment status. """
    def get(self, request, *args, **kwargs):
        dict_response = {'succeeded': Response(data='An email has been sent to you with purchase details',
                                               status=status.HTTP_201_CREATED),
                         'fail': Response(data='There is no data. Contact the manager.',
                                          status=status.HTTP_400_BAD_REQUEST),
                         'not succeeded': Response(data='Not succeeded status. Try later',
                                                   status=status.HTTP_400_BAD_REQUEST)
                         }

        return dict_response[payment_detail(request)]
