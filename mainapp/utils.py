from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from django.conf import settings
from django.core.mail import send_mail
from dotenv import load_dotenv
import logging

def pagination_custom(request,table):
    paginator = Paginator(table, 10)
    page = request.GET.get('page')
    try:
        table = paginator.page(page)
    except PageNotAnInteger:
        table = paginator.page(1)
    except EmptyPage:
        table = paginator.page(paginator.num_pages)
    return table

load_dotenv() 
apikey = os.getenv("SENDGRID_APIKEY")

def send_email_siging(email, subject_content, message_content):
    print('send email function start')
    subject = subject_content
    message = message_content
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email,]
    try:
        send_mail(subject, message, from_email, recipient_list)
        print('send email function success')
    except Exception as e:
        print('An error occurred while sending the email:', e)
    print('send email function end')