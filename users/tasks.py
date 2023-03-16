from typing import Dict

from django.utils import timezone
from datetime import timedelta

from celery import shared_task

from users.models import Buyers, BuyerPaymentPending


@shared_task
def create_buyer(data_payment_for_model: Dict, total_price: int) -> bool:
    products = data_payment_for_model.pop('orders_pending')
    purchases = data_payment_for_model.pop('payment_id')
    created_at = data_payment_for_model.pop('created_at')
    captured_at = data_payment_for_model.pop('captured_at')
    email = data_payment_for_model.pop('email')
    if Buyers.objects.filter(email=email).exists():
        buyer = Buyers.objects.get(email=email)
        buyer.purchases[purchases] = {'created_at': created_at, 'captured_at': captured_at,
                                      'payment_status': data_payment_for_model.pop('payment_status'),
                                      'products': products,
                                      'sum': str(total_price)
                                      }
        buyer.delivery_data[purchases] = {**data_payment_for_model}
        buyer.save()
        return True
    else:
        Buyers.objects.create(email=email,
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
    BuyerPaymentPending.objects.create(**data_payment)


@shared_task
def remove_buyer_payment_pending(status: bool, payment_id: str) -> None:
    if status is True:
        BuyerPaymentPending.objects.filter(payment_id=payment_id).delete()


@shared_task
def remove_data_pending():
    expired_date = timezone.now() - timedelta(days=8)
    BuyerPaymentPending.objects.filter(created_at__lt=expired_date).delete()
