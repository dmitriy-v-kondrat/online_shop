

from users.buyers_data import AddToBuyerPaymentPending, AddToBuyers, DataForPayment, ForBuyersBase


def data_for_buyers(request, buyer):
    checkout_data = DataForPayment(request, buyer).pay_product()
    return checkout_data


def data_payment_pending(request):
    AddToBuyerPaymentPending(request).data_for_buyer_payment_pending()


def payment_detail(request) -> str:
    str_response = AddToBuyers(request).check_payment()
    return str_response
