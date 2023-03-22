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


class ForBuyersBase(object):

    def __init__(self, request):
        self.session = request.session
        self.cart = Cart(request)
        # self.payment = Payment()
        self.products = Product()

    def data_payment(self):
        return Payment.find_one(self.session.get('payment_id'))

    def get_products(self, keys):
        return Product.objects.filter(id__in=keys).only('id', 'name', 'quantity')

    def cart_detail(self):
        return [item for item in self.cart]


class DataForPayment(ForBuyersBase):

    def __init__(self, request, buyer):

        super().__init__(request)
        self.buyer = buyer

    def pay_product(self) -> Dict:
        payments = self.create_payment()
        checkout_data = {"buyer": self.buyer,
                         "cart": self.cart_detail(),
                         "payment_value": payments.amount.value,
                         }
        return checkout_data

    def create_payment(self) -> TypeVar:
        purchase_detail = self.check_product()
        to_payment = Payment.create({
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
            "description": f"{self.buyer['email']}, {self.buyer['first_name']}, {self.buyer['last_name']}",

            }, uuid.uuid4())
        self.update_session(to_payment)
        return to_payment

    def check_product(self) -> Dict:
        purchase_detail = {}
        for product in self.get_products(keys=self.cart.cart.keys()):
            if product.quantity >= self.cart.cart[str(product.id)]['quantity']:
                purchase_detail[str(product.id)] = f"{product.name}, {self.cart.cart[str(product.id)]['quantity']}"
            else:
                raise ValidationError(detail=f"{product.name} left {product.quantity} pieces.")
        return purchase_detail

    def update_session(self, payments: TypeVar) -> None:
        self.session.update({'payment_id': payments.id,
                             'buyer': self.buyer,
                             'to_pay': payments.confirmation.confirmation_url
                             })




class AddToBuyerPaymentPending(ForBuyersBase):

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

    def __init__(self, request):

        super().__init__(request)
        self.payment = self.data_payment()

    def check_payment(self):
        if self.session.get('payment_id'):
            if self.payment.status == 'succeeded':
                if self.add_buyer_data() is True:
                    self.session.flush()
                    return 'succeeded'
            else:
                return 'not succeeded'
        else:
            return 'fail'

    def add_buyer_data(self) -> bool:
        total_price = self.payment.amount.value
        payment_id = self.payment.id
        write_product = self.write_product_for()

        dict_data_payment = self.read_data_payment_pending()
        newsletter_status = dict_data_payment.pop('receive_newsletter')
        dict_data_payment['captured_at'] = self.payment.captured_at
        dict_data_payment['payment_status'] = self.payment.status

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

    def write_product_for(self) -> Tuple:
        product_name = ''
        product_id = ''
        product_pieces = ''
        sales = []
        self.cart_detail()
        Product.objects.bulk_update(  # move in the Celery or another function?
                [Product(id=int(pk),
                         quantity=F('quantity') - int(self.payment.metadata[str(pk)].split(', ')[1]))
                 for pk in self.payment.metadata.keys()
                 ], ['quantity'])
        for pk in self.payment.metadata.keys():
            product_name += self.cart.cart[pk]['product'] + '\n\n'
            product_pieces += str(self.cart.cart[pk]['quantity']) + '\n\n'
            product_id += str(pk) + '\n\n'
            sales.append({"Product": self.cart.cart[pk]['product'],
                          "pieces": str(self.cart.cart[pk]['quantity'])
                          }
                         )
        dict_data_for_csv = {'product_name': product_name, 'product_id': product_id, 'product_pieces': product_pieces}
        return dict_data_for_csv, sales



    def read_data_payment_pending(self) -> Dict:
        buyer = BuyerPaymentPending.objects\
            .filter(payment_id=self.data_payment().id)\
            .values('payment_id', 'created_at',
                    'payment_status', 'first_name',
                    'last_name', 'email',
                    'phone', 'orders_pending',
                    'postal_code', 'country',
                    'state', 'locality',
                    'receive_newsletter'
                    )
        return buyer[0]
