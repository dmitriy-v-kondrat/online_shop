import uuid
from typing import Dict, Tuple, TypeVar

from celery import chain, group
from django.conf import settings
from django.db.models import F
from memory_profiler import profile
from rest_framework.exceptions import ValidationError
from yookassa import Configuration, Payment

from cart.cart import Cart
from cart.tasks import add_csv, add_mail, create_pdf
from shop.models import Product
from users.models import BuyerPaymentPending
from users.tasks import add_buyer_payment_pending, create_buyer, remove_buyer_payment_pending

Configuration.account_id = settings.CONFIGURATION_PAY['payment_account']
Configuration.secret_key = settings.CONFIGURATION_PAY['payment_key']


class ForBuyersBase:

    def __init__(self, request):
        self.session = request.session
        self.cart = Cart(request)
        self.payment = Payment()
        self.products = Product()

    def data_payment(self):
        return self.payment.find_one(self.session.get('payment_id'))

    def get_products(self, keys):
        return Product.objects.filter(id__in=keys).only('id', 'name', 'quantity')

    def cart_detail(self):
        return [item for item in self.cart]


class DataForPayment(ForBuyersBase):

    def pay_product(self, buyer: Dict) -> Dict:
        payments = self.create_payment(buyer)
        checkout_data = {"buyer": buyer,
                         "cart": self.cart_detail(),
                         "payment_value": payments.amount.value,
                         }
        return checkout_data

    def check_product(self) -> Dict:
        purchase_detail = {}
        for product in self.get_products(keys=self.cart.cart.keys()):
            if product.quantity >= self.cart.cart[str(product.id)]['quantity']:
                purchase_detail[str(product.id)] = int(self.cart.cart[str(product.id)]['quantity'])
            else:
                raise ValidationError(detail=f"{product.name} left {product.quantity} pieces.")
        return purchase_detail

    def create_payment(self, buyer: Dict) -> TypeVar:
        purchase_detail = self.check_product()
        payments = self.payment.create({
            "amount": {
                "value": self.cart.get_total_price(),
                "currency": "RUB"
                },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://127.0.0.1:8000/api/v1/cart/payment-detail/"
                },
            "metadata": purchase_detail,
            "capture": True,
            "description": f"{buyer['email']}, {buyer['first_name']}, {buyer['last_name']}",

            }, uuid.uuid4())
        self.update_session(payments, buyer)
        return payments

    def update_session(self, payments: TypeVar, buyer: Dict) -> None:
        self.session.update({'payment_id': payments.id,
                             'buyer': buyer,
                             'to_pay': payments.confirmation.confirmation_url
                             })

    def data_for_buyer_payment_pending(self) -> None:
        data_for_payment = self.data_payment()
        data_payment = {'payment_id': data_for_payment.id,
                        'orders_pending': data_for_payment.metadata,
                        'created_at': data_for_payment.created_at,
                        'payment_status': data_for_payment.status,
                        **self.session.get('buyer')
                        }
        add_buyer_payment_pending.s(data_payment=data_payment).apply_async()


class AddToBuyers(ForBuyersBase):
    @profile
    def write_product_for(self, payment) -> Tuple:
        product_name = ''
        product_id = ''
        product_pieces = ''
        sales = []
        self.cart_detail()
        Product.objects.bulk_update(
                [Product(id=int(pk),
                         quantity=F('quantity') + int((payment.metadata[str(pk)])))
                 for pk in payment.metadata.keys()
                 ], ['quantity'])
        for pk in payment.metadata.keys():
            product_name += self.cart.cart[pk]['product'] + '\n\n'
            product_pieces += str(self.cart.cart[pk]['quantity']) + '\n\n'
            product_id += str(pk) + '\n\n'
            sales.append({"Product": self.cart.cart[pk]['product'],
                          "pieces": str(self.cart.cart[pk]['quantity'])
                          }
                         )
        dict_data_for_csv = {'product_name': product_name, 'product_id': product_id, 'product_pieces': product_pieces}
        return dict_data_for_csv, sales

    def add_buyer_data(self, payment) -> bool:
        total_price = payment.amount.value
        payment_id = payment.id
        write_product = self.write_product_for(payment=payment)

        dict_data_payment = self.read_data_payment_pending()
        newsletter_status = dict_data_payment.pop('receive_newsletter')
        dict_data_payment['captured_at'] = self.data_payment().captured_at
        dict_data_payment['payment_status'] = self.data_payment().status

        if newsletter_status is True:
            data_payment_for_model = dict_data_payment.copy()
            create_buyer.s(data_payment_for_model=data_payment_for_model,
                           total_price=total_price
                           ).apply_async()

        dict_data_payment.pop('orders_pending')
        data_for_csv = {**write_product[0], **dict_data_payment}

        group(
                chain(add_csv.s(data_for_csv=data_for_csv),
                      remove_buyer_payment_pending.s(payment_id=payment_id)),
                chain(create_pdf.s(sales=write_product[1], payment=total_price, payment_id=payment_id),
                      add_mail.s(dict_data_payment=dict_data_payment))
                ).apply_async()

        return True

    @profile
    def read_data_payment_pending(self) -> Dict:
        buyer = BuyerPaymentPending.objects.filter(payment_id=self.data_payment().id).values('payment_id',
                                                                                             'created_at',
                                                                                             'payment_status',
                                                                                             'first_name',
                                                                                             'last_name',
                                                                                             'email',
                                                                                             'phone',
                                                                                             'orders_pending',
                                                                                             'postal_code',
                                                                                             'country',
                                                                                             'state',
                                                                                             'locality',
                                                                                             'receive_newsletter')
        dict_data_payment = buyer[0] #???
        return dict_data_payment
