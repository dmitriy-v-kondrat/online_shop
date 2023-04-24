""" App.users tasks. """

from typing import Dict

from django.utils import timezone
from datetime import timedelta

from celery import shared_task

from users.models import Buyer, BuyerPaymentPending


@shared_task
def create_buyer(data_payment_for_model: Dict, total_price: int) -> bool:
    """ Create model Buyer after succeeded pay."""
    products = data_payment_for_model.pop('orders_pending')
    purchases = data_payment_for_model.pop('payment_id')
    created_at = data_payment_for_model.pop('created_at')
    captured_at = data_payment_for_model.pop('captured_at')
    email = data_payment_for_model.pop('email')
    if Buyer.objects.filter(email=email).exists():
        buyer = Buyer.objects.get(email=email)
        buyer.purchases[purchases] = {'created_at': created_at, 'captured_at': captured_at,
                                      'payment_status': data_payment_for_model.pop('payment_status'),
                                      'products': products,
                                      'sum': str(total_price)
                                      }
        buyer.delivery_data[purchases] = {**data_payment_for_model}
        buyer.save()
        return True
    else:
        Buyer.objects.create(email=email,
                              purchases={purchases: {'created_at': created_at, 'captured_at': captured_at,
                                                     'payment_status': data_payment_for_model.pop('payment_status'),
                                                     'products': products,
                                                     'sum': str(total_price)
                                                     }
                                         },
                              delivery_data={purchases: {**data_payment_for_model
                                                         }
                                             }
                              )
        return True


@shared_task
def add_buyer_payment_pending(data_payment: Dict) -> None:
    """ Create model BuyerPaymentPending. """
    BuyerPaymentPending.objects.create(**data_payment)


@shared_task
def remove_buyer_payment_pending(status: bool, payment_id: str) -> None:
    """ Remove model BuyerPaymentPending. """
    if status is True:
        BuyerPaymentPending.objects.filter(payment_id=payment_id).delete()


@shared_task
def remove_data_pending():
    """ Remove model BuyerPaymentPending after expired date. """
    expired_date = timezone.now() - timedelta(days=8)
    BuyerPaymentPending.objects.filter(created_at__lt=expired_date).delete()
