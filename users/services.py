from shop.models import Product


def purchases_product(purchases: dict) -> str:
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
    products = Product.objects.filter(id__in=dict_product.keys())
    product_name = ''
    for product in products:
        product_name += f"ID: {product.id}  Name: {product.name}  Pieces: {dict_product[str(product.id)]}\n"
    return product_name

# indefined

# purchases_products += f"Order ID: {purchase}\n" \
#                               f"Payment: {purchases[purchase]['payment_status']}\n" \
#                               f"Date payment : {purchases[purchase]['date']}\n" \
#                               f"Product:\n{product_naming(dict_product=purchases[purchase]['products'])}" \
#                               f"Sum: {purchases[purchase]['sum']}\n\n"