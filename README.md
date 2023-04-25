# online_shop
Simple online store RestAPI created with djangorestframework. The store uses the shopping cart
purchases in sessions (cookies). Integrated payment system yookassa,
the ability to integrate other payment systems. With Celery
mailing, CSV writing and model functions run in the background,
which allowed to improve the response time of the pages.

# Structure
*app.cart* - storage of the cart in the session. Add product and 
update quantity and cost. Displays the total cost, deletes the
product and removes the cart from the session. Deletes session 
after payment.

*app.shop* - list of categories, products in category, list
products, a detailed display of the product with the ability to add to
basket. A filter is used to display products by category,
brand, price, discount and product availability.

*app.users* - creates and processes payment data. Saves
to the database and CSV-file information about the order,
writes to the database data info of customers who subscribed 
to the newsletter and paid for the order.

# Requirements

###### Python
###### Django
###### DjangoRestFramework
###### Celery
###### Redis
###### Docker
###### PostgreSQL
