from shop.buyers_data import AddToBuyers, DataForPayment



def data_for_buyers(request, buyer):
    checkout_data = DataForPayment(request).pay_product(buyer=buyer)
    return checkout_data


def data_payment_pending(request):
    DataForPayment(request).data_for_buyer_payment_pending()


def payment_detail(request) -> str:
    if request.session.get('payment_id'):
        payment = AddToBuyers(request).data_payment()
        if payment.status == 'succeeded':
            if AddToBuyers(request).add_buyer_data(payment=payment) is True:
                request.session.flush()
                return 'succeeded'
        else:
            return 'not succeeded'
    else:
        return 'fail'
