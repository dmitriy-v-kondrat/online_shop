""" App.users services. """


def purchases_and_delivery(obj) -> str:
    """ Forming and structural data from JSON field for admin-panel. """
    purchases = obj.purchases
    purchases_delivery = ''
    for purchase in purchases:
        purchases_delivery += f"Order ID: {purchase}\n" \
                                  f"Payment: {purchases[purchase]['payment_status']}\n" \
                                  f"Date created at : {purchases[purchase]['created_at']}\n" \
                                  f"Date captured at : {purchases[purchase]['captured_at']}\n" \
                                  f"Product:\n{product_naming(dict_product=purchases[purchase]['products'])}"\
                                  f"Sum: {purchases[purchase]['sum']}\n" \
                                  f"Delivery:\n {delivery_detail(delivery_data=obj.delivery_data, order_id=purchase)}"\
                                  f"\n\n"

    return purchases_delivery


def product_naming(dict_product: dict) -> str:
    """ Forming product name. """
    product_name = ''
    for pk in dict_product:
        product_name += f"ID: {pk}"\
                        f"  Name: {dict_product[pk].split(', ')[0]}" \
                        f"  Pieces: {dict_product[pk].split(', ')[1]}\n"
    return product_name


def delivery_detail(delivery_data: dict, order_id: str) -> str:
    """ Forming delivery address. """
    return "\n ".join(f"{k}: {v}" for k, v in delivery_data[order_id].items())
