import csv
import json
import os
from typing import Dict
from datetime import datetime

from celery import shared_task
from django.conf import settings
from fpdf import FPDF
from django.core.mail import EmailMessage


@shared_task
def add_pre_payment(pre_payment_data):
    with open(f"media/files/orders/[{datetime.now()}].json", 'a') as json_file:
        json_file.write(json.dumps(pre_payment_data) + '\n')


@shared_task
def add_csv(data_for_csv: Dict) -> bool:
    fieldnames = ['created_at', 'captured_at', 'payment_status',
                  'payment_id', 'product_name',
                  'product_id', 'product_pieces',
                  'first_name',
                  'last_name', 'email',
                  'phone', 'postal_code',
                  'country', 'state', 'locality'
                  ]
    with open('media/files/orders/orderings.csv', 'a', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, dialect='excel')
        writer.writerow(data_for_csv)
    return True


@shared_task
def remove_pre_payment(status, payment_id):
    if status is True:
        with open('media/files/orders/pre_payment.json', 'r') as json_file:
            data = json.loads("[" + json_file.read().replace("}\n{", "},\n{") + "]")
        for pre_payment_data in data:
            if payment_id in pre_payment_data['payment_id']:
                data.pop(data.index(pre_payment_data))
        with open('media/files/orders/pre_payment.json', 'w') as json_file:
            for new_payment_data in data:
                json_file.write(json.dumps(new_payment_data) + '\n')
        return True

@shared_task
def create_pdf(sales, payment, payment_id):
    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('courier', 'B', 16)
    pdf.cell(40, 10, 'Purchasing from online shop:', 0, 1)
    pdf.cell(40, 10, '', 0, 1)
    pdf.set_font('courier', '', 12)
    pdf.cell(200, 8, f"{'Product'.ljust(30)} {'pieces'.rjust(20)}", 0, 1)
    pdf.line(10, 30, 150, 30)
    pdf.line(10, 38, 150, 38)
    for line in sales:
        pdf.cell(200, 8, f"{line['Product'].ljust(30)} {line['pieces'].rjust(20)}", 0, 1)
    pdf.cell(200, 8, f"{'Total Sum:'.ljust(30)} {str(payment).rjust(20)}", 0, 1)
    pdf.output(f"media/files/pdf/{payment_id}.pdf", 'UTF-8')
    return payment_id


@shared_task
def add_mail(payment_id, dict_data_payment: Dict) -> None:
    subject = 'Purchasing from online shop'
    content = f"Dear {dict_data_payment['first_name']} {dict_data_payment['last_name']}," \
              f" thank you for purchasing goods in our store. Details in attached pdf file."
    mail = EmailMessage(subject, content, settings.EMAIL_HOST_USER, [dict_data_payment['email']])
    mail.attach_file(f"media/files/pdf/{payment_id}.pdf", "application/pdf")
    mail.send()
    path = f"media/files/pdf/{payment_id}.pdf"
    os.remove(path)
