

def get_purchase_delivery(purchases: dict) -> str:
    purchases_products = ''
    for purchase in purchases:
        purchases_products += f"Order ID: {purchase}\n" \
                              f"Payment: {purchases[purchase]['payment_status']}\n" \
                              f"Date created at : {purchases[purchase]['created_at']}\n" \
                              f"Date captured at : {purchases[purchase]['captured_at']}\n" \
                              f"Product:\n{product_naming(dict_product=purchases[purchase]['products'])}" \
                              f"Sum: {purchases[purchase]['sum']}\n\n"

    return purchases_products


def product_naming(dict_product: dict) -> str:
    product_name = ''
    for pk in dict_product:
        product_name += f"ID: {pk}" \
                        f"  Name: {dict_product[pk].split(', ')[0]}" \
                        f"  Pieces: {dict_product[pk].split(', ')[1]}\n"
    return product_name
