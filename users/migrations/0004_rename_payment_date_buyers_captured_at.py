# Generated by Django 4.1.3 on 2023-02-03 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_buyerpaymentpending_buyers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buyers',
            old_name='payment_date',
            new_name='captured_at',
        ),
    ]
