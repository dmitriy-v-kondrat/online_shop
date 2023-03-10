from typing import Dict

from django.utils import timezone
from datetime import timedelta

from celery import shared_task
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from users.models import Buyers, BuyerPaymentPending


@shared_task
def create_buyer(data_payment_for_model: Dict, total_price: int) -> bool:
    products = data_payment_for_model.pop('orders_pending')
    purchases = data_payment_for_model.pop('payment_id')
    created_at = data_payment_for_model.pop('created_at')
    captured_at = data_payment_for_model.pop('captured_at')
    if Buyers.objects.filter(email=data_payment_for_model['email']).exists():
        buyer = Buyers.objects.get(email=data_payment_for_model.pop('email'))
        buyer.purchases[purchases] = {'created_at': created_at, 'captured_at': captured_at,
                                      'payment_status': data_payment_for_model.pop('payment_status'),
                                      'products': products,
                                      'sum': str(total_price)
                                      }
        buyer.first_name = data_payment_for_model['first_name']
        buyer.last_name = data_payment_for_model['last_name']
        buyer.phone = data_payment_for_model['phone']
        buyer.postal_code = data_payment_for_model['postal_code']
        buyer.country = data_payment_for_model['country']
        buyer.state = data_payment_for_model['state']
        buyer.locality = data_payment_for_model['locality']
        buyer.save()
        return True
    else:
        Buyers.objects.create(purchases={purchases: {'created_at': created_at, 'captured_at': captured_at,
                                                     'payment_status': data_payment_for_model.pop('payment_status'),
                                                     'products': products,
                                                     'sum': str(total_price)
                                                     }
                                         }, **data_payment_for_model
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
