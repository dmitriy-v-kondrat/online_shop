""" Celery tasks. """
import csv
import os
from typing import Dict, List

from celery import shared_task
from django.conf import settings
from fpdf import FPDF
from django.core.mail import EmailMessage


@shared_task
def add_csv(data_for_csv: Dict) -> bool:
    """ Writing in CSV-file. """
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
def create_pdf(sales: List, payment: int, payment_id: int) -> int:
    """ Create PDF-file for sent in email attachment. """
    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('courier', 'B', 16)
    pdf.cell(40, 10, 'Purchasing from online shop:', 0, 1)
    pdf.cell(40, 10, '', 0, 1)
    pdf.set_font('courier', '', 12)
    pdf.cell(287, 8, f"{'Product'.ljust(75)} {'pieces'.rjust(30)}", 0, 1)
    pdf.line(10, 30, 287, 30)
    pdf.line(10, 38, 287, 38)
    for line in sales:
        pdf.cell(287, 8, f"{line['Product'].ljust(75)} {line['pieces'].rjust(30)}", 0, 1,)
    pdf.cell(287, 8, f"{'Total Sum:'.ljust(75)} {str(payment).rjust(30)}", 0, 1)
    pdf.output(f"media/files/pdf/{payment_id}.pdf", 'UTF-8')
    return payment_id


@shared_task
def add_mail(payment_id: int, dict_data_payment: Dict) -> None:
    """ Send email and remove PDF-file. """
    subject = 'Purchasing from online shop'
    content = f"Dear {dict_data_payment['first_name']} {dict_data_payment['last_name']}," \
              f" thank you for purchasing goods in our store. Details in attached pdf file."
    mail = EmailMessage(subject, content, settings.EMAIL_HOST_USER, [dict_data_payment['email']])
    mail.attach_file(f"media/files/pdf/{payment_id}.pdf", "application/pdf")
    mail.send()
    path = f"media/files/pdf/{payment_id}.pdf"
    os.remove(path)
